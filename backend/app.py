
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from auth_db import create_users_table, get_connection
import joblib
import numpy as np
import json
from otp_utils import generate_otp, otp_expiry
from auth_db import create_otp_table
import time
import jwt
import datetime
import sqlite3
import os
import pickle
from pdf_utils import extract_data_from_pdf
from health_utils import get_default_values, calculate_risk_level, get_clinical_summary
from report_generator import generate_pdf_report
from flask import send_file


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize DB
create_users_table()
create_otp_table()

# Load ML models
diabetes_model = joblib.load("../models/diabetes_model.pkl")
diabetes_scaler = joblib.load("../models/diabetes_scaler.pkl")

heart_model = joblib.load("../models/heart_disease_model.pkl")
heart_scaler = joblib.load("../models/heart_disease_scaler.pkl")

with open("../models/heart_features.json", "r") as f:
    heart_features = json.load(f)


# ---------- HOME ----------
@app.route("/")
def home():
    return "Healthcare Prediction API is running"


# ---------- SIGNUP ----------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json

    first_name = data.get("firstName")
    last_name = data.get("lastName")
    dob = data.get("dob")
    email = data.get("email")
    phone = data.get("phone")
    city = data.get("city")
    pincode = data.get("pincode")
    password = generate_password_hash(data.get("password"))
    role = data.get("role", "patient") # Default to patient

    conn = get_connection()
    cursor = conn.cursor()

    # Check existing user
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "User already exists"}), 400

    # Insert user (not verified yet)
    cursor.execute("""
        INSERT INTO users 
        (first_name, last_name, dob, email, phone, city, pincode, password, is_verified, role)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
    """, (first_name, last_name, dob, email, phone, city, pincode, password, role))

    # Generate OTP
    otp = generate_otp()
    expiry = otp_expiry()

    cursor.execute(
        "INSERT INTO otp_codes (phone, otp, expires_at) VALUES (?, ?, ?)",
        (phone, otp, expiry)
    )

    conn.commit()
    conn.close()

    print(f"OTP for {phone} is {otp}")  # MOCK SMS

    return jsonify({"message": "OTP sent successfully"})


import time
import jwt

JWT_SECRET = "supersecretkey"   # later move to env
JWT_EXPIRY_SECONDS = 60 * 60    # 1 hour

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    phone = data.get("phone")
    otp = data.get("otp")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT otp, expires_at FROM otp_codes
        WHERE phone = ?
        ORDER BY id DESC LIMIT 1
    """, (phone,))

    record = cursor.fetchone()

    if not record:
        conn.close()
        return jsonify({"error": "OTP not found"}), 400

    saved_otp, expires_at = record

    if time.time() > expires_at:
        conn.close()
        return jsonify({"error": "OTP expired"}), 400

    if otp != saved_otp:
        conn.close()
        return jsonify({"error": "Invalid OTP"}), 400

    # Mark user verified
    cursor.execute("""
        UPDATE users SET is_verified = 1 WHERE phone = ?
    """, (phone,))

    # Fetch user details to return to frontend
    cursor.execute("SELECT first_name, last_name, email FROM users WHERE phone = ?", (phone,))
    user = cursor.fetchone()
    
    conn.commit()
    conn.close()

    # Generate JWT
    token = jwt.encode(
        {
            "phone": phone,
            "exp": time.time() + JWT_EXPIRY_SECONDS
        },
        JWT_SECRET,
        algorithm="HS256"
    )

    return jsonify({
        "message": "OTP verified",
        "token": token,
        "user": {
            "first_name": user[0],
            "last_name": user[1],
            "email": user[2]
        }
    })



# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    email = data.get("email")
    password = data.get("password")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name, password, role FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not check_password_hash(user[3], password):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "first_name": user[1],
            "last_name": user[2],
            "email": email,
            "role": user[4]  # role column
        }
    })


# ---------- DIABETES PREDICTION ----------
# ---------- DIABETES PREDICTION ----------
@app.route("/predict/diabetes", methods=["POST"])
def predict_diabetes():
    pdf_data = {}
    form_data = {}
    
    # 1. Handle File Upload (PDF)
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            filepath = os.path.join("temp_uploads", file.filename)
            os.makedirs("temp_uploads", exist_ok=True)
            file.save(filepath)
            pdf_data = extract_data_from_pdf(filepath)
            os.remove(filepath)

    # 2. Get Manual Input
    if request.form:
        form_data = request.form.to_dict()
    elif request.json:
        form_data = request.json
    
    email = form_data.get("email")

    # 3. Get Defaults
    defaults = get_default_values("diabetes")
    
    # Helper for Strict Priority: PDF > User > Default
    input_details = {} 
    # structured as { feature_name: { value: val, source: "Report"|"User"|"Estimated" } }
    
    def resolve_value(keys, default_key):
        # 1. Check PDF
        for k in keys:
            if k in pdf_data and pdf_data[k] not in [None, ""]:
                try:
                    return float(pdf_data[k]), "Report"
                except: pass
        
        # 2. Check User Input
        for k in keys:
            if k in form_data and form_data[k] not in [None, ""]:
                try:
                    return float(form_data[k]), "User"
                except: pass
                
        # 3. Default
        return float(defaults.get(default_key, 0)), "Estimated"

    # Define Feature Mapping
    feature_map = {
        "Pregnancies": (["Pregnancies", "pregnancies"], "pregnancies"),
        "Glucose": (["Glucose", "glucose"], "glucose"),
        "BloodPressure": (["BloodPressure", "blood_pressure", "bp", "bloodpressure"], "bloodpressure"),
        "SkinThickness": (["SkinThickness", "skin_thickness", "skinthickness"], "skinthickness"),
        "Insulin": (["Insulin", "insulin"], "insulin"),
        "BMI": (["BMI", "bmi"], "bmi"),
        "DiabetesPedigreeFunction": (["DiabetesPedigreeFunction", "dpf", "diabetespedigreefunction"], "diabetespedigreefunction"),
        "Age": (["Age", "age"], "age")
    }

    final_values = []
    simple_input_data = {} # For charts/compatibility
    
    for name, (keys, default_key) in feature_map.items():
        val, src = resolve_value(keys, default_key)
        
        # Gender Check: Force pregnancies to 0 if gender is Male
        gender = form_data.get("gender", pdf_data.get("sex"))
        if name == "Pregnancies":
            # Check profile as well if not provided
            if not gender and email:
                 conn = get_connection()
                 c = conn.cursor()
                 c.execute("SELECT gender FROM users WHERE email = ?", (email,))
                 u = c.fetchone()
                 if u: gender = u[0]
                 conn.close()
            
            if gender and str(gender).lower() in ["male", "1"]:
                val = 0.0
                src = "Gender Default (Male)"

        input_details[name] = {"value": val, "source": src}
        simple_input_data[name] = val
        final_values.append(val)
    
    # 4. Predict
    input_arr = np.array(final_values).reshape(1, -1)
    scaled_input = diabetes_scaler.transform(input_arr)
    
    prediction = diabetes_model.predict(scaled_input)[0]
    prob = diabetes_model.predict_proba(scaled_input)[0][1] * 100
    
    # 5. Analysis
    result = "Diabetic" if prediction == 1 else "Non-Diabetic"
    risk_level = calculate_risk_level(prob)
    
    # Consistency Check: Model overrides Report
    # (Here we don't have an explicit 'report label' passed, but implied logic is Model is Truth)
    
    summary = get_clinical_summary("diabetes", simple_input_data, risk_level)
    
    return jsonify({
        "prediction": result,
        "probability": round(prob, 2),
        "risk_level": risk_level,
        "clinical_summary": summary,
        "recommended_department": "Endocrinology" if prediction == 1 else "General",
        "input_data": simple_input_data,
        "input_details": input_details,
        "patient_name": pdf_data.get("name"), # Return extracted name
        "patient_sex": pdf_data.get("sex") # Return extracted sex
    })


# ---------- HEART PREDICTION ----------
@app.route("/predict/heart", methods=["POST"])
def predict_heart():
    pdf_data = {}
    form_data = {}
    
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            filepath = os.path.join("temp_uploads", file.filename)
            os.makedirs("temp_uploads", exist_ok=True)
            file.save(filepath)
            pdf_data = extract_data_from_pdf(filepath)
            os.remove(filepath)

    if request.form:
        form_data = request.form.to_dict()
    elif request.json:
        form_data = request.json
    
    email = form_data.get("email")

    defaults = get_default_values("heart")
    
    input_details = {}
    
    def resolve_value(keys, default_key):
        for k in keys:
            if k in pdf_data and pdf_data[k] not in [None, ""]:
                try: 
                    return float(pdf_data[k]), "Report"
                except: pass
        for k in keys:
            if k in form_data and form_data[k] not in [None, ""]:
                try:
                    return float(form_data[k]), "User"
                except: pass
        return float(defaults.get(default_key, 0)), "Estimated"

    # Feature Mapping (Order matters for model!)
    # age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
    feature_config = [
        ("age", (["Age", "age"], "age")),
        ("sex", (["Sex", "sex"], "sex")),
        ("cp", (["CP", "cp", "chest_pain"], "cp")),
        ("trestbps", (["Trestbps", "trestbps", "blood_pressure", "bp"], "trestbps")),
        ("chol", (["Chol", "chol", "cholesterol"], "chol")),
        ("fbs", (["FBS", "fbs", "fasting_blood_sugar"], "fbs")),
        ("restecg", (["RestECG", "restecg"], "restecg")),
        ("thalach", (["Thalach", "thalach", "max_heart_rate"], "thalach")),
        ("exang", (["Exang", "exang", "exercise_angina"], "exang")),
        ("oldpeak", (["Oldpeak", "oldpeak", "st_depression"], "oldpeak")),
        ("slope", (["Slope", "slope"], "slope")),
        ("ca", (["CA", "ca", "major_vessels"], "ca")),
        ("thal", (["Thal", "thal", "thalassemia"], "thal"))
    ]
    
    final_values = []
    simple_input_data = {}
    
    for name, (keys, default_key) in feature_config:
        val, src = resolve_value(keys, default_key)
        input_details[name] = {"value": val, "source": src}
        simple_input_data[name] = val
        final_values.append(val)
        
    input_arr = np.array(final_values).reshape(1, -1)
    scaled_input = heart_scaler.transform(input_arr)
    
    prediction = heart_model.predict(scaled_input)[0]
    prob = heart_model.predict_proba(scaled_input)[0][1] * 100
    
    result = "Heart Disease Detected" if prediction == 1 else "No Heart Disease"
    risk_level = calculate_risk_level(prob)
    summary = get_clinical_summary("heart", simple_input_data, risk_level)
    
    return jsonify({
        "prediction": result,
        "probability": round(prob, 2),
        "risk_level": risk_level,
        "clinical_summary": summary,
        "recommended_department": "Cardiology" if prediction == 1 else "General",
        "input_data": simple_input_data,
        "input_details": input_details,
        "patient_name": pdf_data.get("name"), # Return extracted name
        "patient_sex": pdf_data.get("sex") # Return extracted sex
    })



# ---------- PROFILE MANAGEMENT ----------
# Legacy profile route removed to avoid conflicts with /api/user/profile
# @app.route("/profile", methods=["GET", "PUT"])
# def profile():
#     ... (code commented out) ...
#     return jsonify({"message": "Deprecated"})


@app.route("/change-password", methods=["POST"])
def change_password():
    data = request.json
    email = data.get("email")
    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404
        
    if not check_password_hash(user[0], current_password):
        conn.close()
        return jsonify({"error": "Incorrect current password"}), 401
        
    new_hash = generate_password_hash(new_password)
    
    cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_hash, email))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Password updated successfully"})


# ---------- HOSPITAL & APPOINTMENT LOGIC ----------

import math

# ... (rest of imports)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@app.route("/hospitals", methods=["GET"])
def get_hospitals():
    dept = request.args.get("department")
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    search = request.args.get("search", "").lower()

    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, name, address, lat, lng, departments FROM hospitals WHERE 1=1"
    params = []
    
    if dept:
        query += " AND departments LIKE ?"
        params.append(f'%"{dept}"%')
    
    if search:
        query += " AND (lower(name) LIKE ? OR lower(address) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    cursor.execute(query, params)
    
    hospitals = []
    for row in cursor.fetchall():
        h_id, name, address, h_lat, h_lng, depts = row
        
        # Calculate distance if user location provided
        dist = None
        if lat and lng:
            dist = haversine(lat, lng, h_lat, h_lng)
            
        hospitals.append({
            "id": h_id,
            "name": name,
            "address": address,
            "lat": h_lat,
            "lng": h_lng,
            "departments": json.loads(depts),
            "distance": round(dist, 2) if dist is not None else None
        })
    
    conn.close()
    
    # Sort by distance if available, otherwise by name
    if lat and lng:
        hospitals.sort(key=lambda x: x["distance"] if x["distance"] is not None else float('inf'))
        
    return jsonify(hospitals)

@app.route("/doctors", methods=["GET"])
def get_doctors():
    hosp_id = request.args.get("hospital_id")
    dept = request.args.get("department")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT d.id, u.first_name, u.last_name, d.department, d.specialty, d.experience, d.availability, d.hospital_id, u.email
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        WHERE 1=1
    """
    params = []
    if hosp_id:
        query += " AND d.hospital_id = ?"
        params.append(hosp_id)
    if dept:
        query += " AND d.department = ?"
        params.append(dept)
        
    cursor.execute(query, params)
    doctors = []
    for row in cursor.fetchall():
        doctors.append({
            "id": row[0],
            "name": f"{row[1]} {row[2]}",
            "department": row[3],
            "specialty": row[4],
            "experience": row[5],
            "availability": json.loads(row[6]),
            "hospitalId": row[7],
            "email": row[8] # Exposed for demo
        })
    conn.close()
    return jsonify(doctors)

@app.route("/bookings", methods=["POST"])
def book_appointment():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check for double booking
    cursor.execute("""
        SELECT id FROM appointments 
        WHERE doctor_id = ? AND date = ? AND time_slot = ? AND status != 'Rejected'
    """, (data['doctorId'], data['date'], data['timeSlot']))
    
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Slot already booked"}), 400
        
    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, hospital_id, date, time_slot)
        VALUES ((SELECT id FROM users WHERE email = ?), ?, ?, ?, ?)
    """, (data['patientEmail'], data['doctorId'], data['hospitalId'], data['date'], data['timeSlot']))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Appointment booked successfully", "status": "Pending Confirmation"})

@app.route("/appointments", methods=["GET"])
def get_appointments():
    email = request.args.get("email")
    role = request.args.get("role")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if role == "doctor":
        query = """
            SELECT a.id, u.first_name, u.last_name, a.date, a.time_slot, a.status, h.name
            FROM appointments a
            JOIN users u ON a.patient_id = u.id
            JOIN hospitals h ON a.hospital_id = h.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users ud ON d.user_id = ud.id
            WHERE ud.email = ?
        """
    else:
        query = """
            SELECT a.id, ud.first_name, ud.last_name, a.date, a.time_slot, a.status, h.name
            FROM appointments a
            JOIN hospitals h ON a.hospital_id = h.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users ud ON d.user_id = ud.id
            JOIN users up ON a.patient_id = up.id
            WHERE up.email = ?
        """
        
    cursor.execute(query, (email,))
    apps = []
    for row in cursor.fetchall():
        apps.append({
            "id": row[0],
            "name": f"{row[1]} {row[2]}",
            "date": row[3],
            "time": row[4],
            "status": row[5],
            "hospital": row[6]
        })
    conn.close()
    return jsonify(apps)

@app.route("/appointment/status", methods=["PUT"])
def update_appointment_status():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get doctor name for the notification
    cursor.execute("""
        SELECT ud.first_name, ud.last_name, up.email, h.name, a.date
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users ud ON d.user_id = ud.id
        JOIN users up ON a.patient_id = up.id
        JOIN hospitals h ON a.hospital_id = h.id
        WHERE a.id = ?
    """, (data['id'],))
    info = cursor.fetchone()

    cursor.execute("UPDATE appointments SET status = ? WHERE id = ?", (data['status'], data['id']))
    conn.commit()
    conn.close()

    if info:
        msg = f"Your appointment with Dr. {info[0]} {info[1]} at {info[3]} on {info[4]} is {data['status'].lower()}."
        socketio.emit('notification', {'message': msg, 'email': info[2]})

    return jsonify({"message": "Status updated"})





# ---------- REPORT GENERATION ----------
@app.route("/generate_report", methods=["POST"])
def generate_report():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    patient_data = data.get("patient_data", {})
    prediction = data.get("prediction", "Unknown")
    risk = data.get("risk_level", "Unknown")
    summary = data.get("clinical_summary", "")
    disease = data.get("disease_type", "General")
    email = data.get("email")
    patient_name = data.get("patient_name")
    gender = data.get("gender")
    
    try:
        # If no patient_name or gender provided, try to fetch from user profile
        if (not patient_name or not gender) and email:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT first_name, last_name, gender FROM users WHERE email = ?", (email,))
            u = cursor.fetchone()
            if u:
                if not patient_name:
                    patient_name = f"{u[0]} {u[1]}"
                if not gender:
                    gender = u[2]
            conn.close()

        if not patient_name:
            patient_name = "Guest Patient"

        pdf_path = generate_pdf_report(patient_data, prediction, risk, summary, disease, patient_name, gender)
        
        # Save to History
        if email:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if user:
                user_id = user[0]
                date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                try:
                    cursor.execute("""
                        INSERT INTO reports (user_id, disease_type, prediction, risk_level, date, pdf_path)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, disease, prediction, risk, date_str, pdf_path))
                    conn.commit()
                except Exception as e:
                    print(f"Error saving history: {e}")
            conn.close()

        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({"error": "Failed to generate report"}), 500

# ---------- USER HISTORY ----------
@app.route("/api/user/reports", methods=["GET"])
def get_user_reports():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT r.id, r.disease_type, r.prediction, r.risk_level, r.date, r.pdf_path
        FROM reports r
        JOIN users u ON r.user_id = u.id
        WHERE u.email = ?
        ORDER BY r.id DESC
    """, (email,))
    
    reports = []
    for row in cursor.fetchall():
        reports.append({
            "id": row[0],
            "disease_type": row[1],
            "prediction": row[2],
            "risk_level": row[3],
            "date": row[4],
            "pdf_path": row[5]
        })
    conn.close()
    return jsonify(reports)

# ---------- PROFILE MANAGEMENT ----------
@app.route("/api/user/profile", methods=["GET", "PUT"])
def manage_profile():
    email = request.args.get("email")
    if not email and request.method == "PUT":
        email = request.json.get("email")
            
    if not email:
        return jsonify({"error": "Email required"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "GET":
        cursor.execute("""
            SELECT first_name, last_name, email, phone, city, dob, pincode, address, age, weight, height, profile_pic, gender 
            FROM users WHERE email = ?
        """, (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return jsonify({
                "firstName": row[0],
                "lastName": row[1],
                "email": row[2],
                "phone": row[3],
                "city": row[4],
                "dob": row[5],
                "pincode": row[6],
                "address": row[7],
                "age": row[8],
                "weight": row[9],
                "height": row[10],
                "profilePic": row[11],
                "gender": row[12]
            })
        return jsonify({"error": "User not found"}), 404

    elif request.method == "PUT":
        data = request.json
        cursor.execute("""
            UPDATE users 
            SET first_name = ?, last_name = ?, phone = ?, city = ?, dob = ?, pincode = ?, address = ?, age = ?, weight = ?, height = ?, profile_pic = ?, gender = ?
            WHERE email = ?
        """, (
            data.get("firstName"), 
            data.get("lastName"), 
            data.get("phone"), 
            data.get("city"), 
            data.get("dob"), 
            data.get("pincode"), 
            data.get("address"), 
            data.get("age"), 
            data.get("weight"), 
            data.get("height"), 
            data.get("profilePic"),
            data.get("gender"),
            email
        ))
        conn.commit()
        conn.close()
        return jsonify({"message": "Profile updated"})

if __name__ == "__main__":
    socketio.run(app, debug=True, use_reloader=True, host='0.0.0.0', port=5000)
