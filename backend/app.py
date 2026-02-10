from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from dotenv import load_dotenv
import os
import joblib
import numpy as np
import json
import time
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_file

# Local Imports
from otp_utils import generate_otp, otp_expiry
from pdf_utils import extract_data_from_pdf
from email_service import send_report_email, send_appointment_email, send_otp_email, send_welcome_email
from health_utils import get_default_values, calculate_risk_level, get_clinical_summary
from report_generator import generate_pdf_report
from models import db, User, Hospital, Doctor, Appointment, Notification, Report, OTP, Message

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///users.db") # Fallback for dev if needed, but prefer Postgres
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize Tables (if not exist)
with app.app_context():
    db.create_all()

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
    return "Healthcare Prediction API is running (PostgreSQL)"

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
    role = data.get("role", "patient")

    # Check existing user
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    # Create new user
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        dob=dob,
        email=email,
        phone=phone,
        city=city,
        pincode=pincode,
        password=password,
        role=role,
        is_verified=0
    )
    db.session.add(new_user)
    db.session.commit()

    # Generate OTP
    otp_code = generate_otp()
    expiry = otp_expiry()

    new_otp = OTP(phone=phone, otp=otp_code, expires_at=expiry)
    db.session.add(new_otp)
    db.session.commit()

    print(f"OTP for {phone} is {otp_code}")  # MOCK SMS
    
    # Send OTP Email
    # Note: Signup receives email, but we associated phone with OTP. Ideally send to email too if we use email for OTP.
    # User asked to send to user mail.
    if email:
         send_otp_email(email, otp_code)

    return jsonify({"message": "OTP sent successfully"})

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_EXPIRY_SECONDS = 60 * 60    # 1 hour

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    phone = data.get("phone")
    otp_input = data.get("otp")

    # Get latest OTP
    otp_record = OTP.query.filter_by(phone=phone).order_by(OTP.id.desc()).first()

    if not otp_record:
        return jsonify({"error": "OTP not found"}), 400

    if time.time() > otp_record.expires_at:
        return jsonify({"error": "OTP expired"}), 400

    if otp_input != otp_record.otp:
        return jsonify({"error": "Invalid OTP"}), 400

    # Mark user verified
    user = User.query.filter_by(phone=phone).first()
    if user:
        user.is_verified = 1
        db.session.commit()

        # Generate JWT
        token = jwt.encode(
            {
                "phone": phone,
                "exp": time.time() + JWT_EXPIRY_SECONDS
            },
            JWT_SECRET,
            algorithm="HS256"
        )

        # Send Welcome Email
        send_welcome_email(user.email, user.first_name)

        return jsonify({
            "message": "OTP verified",
            "token": token,
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
        })
    return jsonify({"error": "User not found"}), 404

# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role
        }
    })

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
                 user = User.query.filter_by(email=email).first()
                 if user and user.gender:
                     gender = user.gender
            
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
    
    summary = get_clinical_summary("diabetes", simple_input_data, risk_level)
    
    return jsonify({
        "prediction": result,
        "probability": round(prob, 2),
        "risk_level": risk_level,
        "clinical_summary": summary,
        "recommended_department": "Endocrinology" if prediction == 1 else "General",
        "input_data": simple_input_data,
        "input_details": input_details,
        "patient_name": pdf_data.get("name"),
        "patient_sex": pdf_data.get("sex") 
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
        "patient_name": pdf_data.get("name"), 
        "patient_sex": pdf_data.get("sex") 
    })

@app.route("/change-password", methods=["POST"])
def change_password():
    data = request.json
    email = data.get("email")
    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")

    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    if not check_password_hash(user.password, current_password):
        return jsonify({"error": "Incorrect current password"}), 401
        
    user.password = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({"message": "Password updated successfully"})

# ---------- HOSPITAL & APPOINTMENT LOGIC ----------
import math

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

    query = Hospital.query
    
    if dept:
        # Note: SQLite check was simpler, here assumes departments string contains the substring
        query = query.filter(Hospital._departments.like(f'%"{dept}"%'))
    
    if search:
        query = query.filter((db.func.lower(Hospital.name).like(f"%{search}%")) | (db.func.lower(Hospital.address).like(f"%{search}%")))

    hospitals_db = query.all()
    
    hospitals = []
    for h in hospitals_db:
        dist = None
        if lat and lng and h.lat and h.lng:
            dist = haversine(lat, lng, h.lat, h.lng)
            
        hospitals.append({
            "id": h.id,
            "name": h.name,
            "address": h.address,
            "lat": h.lat,
            "lng": h.lng,
            "departments": h.departments,
            "distance": round(dist, 2) if dist is not None else None
        })
    
    if lat and lng:
        hospitals.sort(key=lambda x: x["distance"] if x["distance"] is not None else float('inf'))
        
    return jsonify(hospitals)

@app.route("/doctors", methods=["GET"])
def get_doctors():
    hosp_id = request.args.get("hospital_id")
    dept = request.args.get("department")
    
    query = Doctor.query.join(User).add_columns(User.first_name, User.last_name, User.email)
    
    if hosp_id:
        query = query.filter(Doctor.hospital_id == hosp_id)
    if dept:
        query = query.filter(Doctor.department == dept)
        
    results = query.all()
    doctors = []
    
    for doc, first_name, last_name, email in results:
        doctors.append({
            "id": doc.id,
            "name": f"{first_name} {last_name}",
            "department": doc.department,
            "specialty": doc.specialty,
            "experience": doc.experience,
            "availability": doc.availability,
            "hospitalId": doc.hospital_id,
            "email": email
        })
    return jsonify(doctors)

@app.route("/bookings", methods=["POST"])
def book_appointment():
    data = request.json
    
    # Check for double booking
    existing = Appointment.query.filter_by(
        doctor_id=data['doctorId'], 
        date=data['date'], 
        time_slot=data['timeSlot']
    ).filter(Appointment.status != 'Rejected').first()
    
    if existing:
        return jsonify({"error": "Slot already booked"}), 400
        
    # Get Patient ID
    patient = User.query.filter_by(email=data['patientEmail']).first()
    if not patient:
         return jsonify({"error": "Patient not found"}), 404

    new_app = Appointment(
        patient_id=patient.id,
        doctor_id=data['doctorId'],
        hospital_id=data['hospitalId'],
        date=data['date'],
        time_slot=data['timeSlot']
    )
    db.session.add(new_app)
    db.session.commit()

    try:
        # Fetch details for email
        doctor = Doctor.query.get(data['doctorId'])
        hospital = Hospital.query.get(data['hospitalId'])
        doc_user = User.query.get(doctor.user_id)
        
        doctor_name = f"{doc_user.first_name} {doc_user.last_name}"
        hospital_name = hospital.name
        lat, lng = hospital.lat, hospital.lng
        
        email_details = {
            "doctor_name": doctor_name,
            "hospital_name": hospital_name,
            "date": data['date'],
            "time": data['timeSlot'],
            "lat": lat,
            "lng": lng
        }
        
        print(f"📧 Sending appointment confirmation for {data['patientEmail']}...")
        print(f"📧 Sending appointment confirmation for {data['patientEmail']}...")
        send_appointment_email(data['patientEmail'], email_details, status="Pending Confirmation")
    except Exception as e:
        print(f"❌ Failed to send appointment email: {e}")

    return jsonify({"message": "Appointment booked successfully", "status": "Pending Confirmation"})

@app.route("/appointments", methods=["GET"])
def get_appointments():
    email = request.args.get("email")
    role = request.args.get("role")
    
    print(f"DEBUG: Fetching appointments for Email: {email}, Role: {role}")

    apps = []
    
    if role == "doctor":
        # JOIN appointments a, users u (patient), hospitals h, doctors d, users ud (doctor)
        # Alias is better.
        DoctorUser = db.aliased(User)
        PatientUser = db.aliased(User)
        
        results = db.session.query(Appointment, PatientUser, Hospital)\
            .join(PatientUser, Appointment.patient_id == PatientUser.id)\
            .join(Hospital, Appointment.hospital_id == Hospital.id)\
            .join(Doctor, Appointment.doctor_id == Doctor.id)\
            .join(DoctorUser, Doctor.user_id == DoctorUser.id)\
            .filter(DoctorUser.email == email).all()

        for appt, patient, hosp in results:
             apps.append({
                "id": appt.id,
                "name": f"{patient.first_name} {patient.last_name}",
                "patientId": patient.id,
                "date": appt.date,
                "time": appt.time_slot,
                "status": appt.status,
                "hospital": hosp.name
            })

    else:
        # Patient View
        DoctorUser = db.aliased(User)
        
        results = db.session.query(Appointment, DoctorUser, Hospital)\
            .join(Doctor, Appointment.doctor_id == Doctor.id)\
            .join(DoctorUser, Doctor.user_id == DoctorUser.id)\
            .join(Hospital, Appointment.hospital_id == Hospital.id)\
            .join(User, Appointment.patient_id == User.id)\
            .filter(User.email == email).all()
            
        for appt, doc_user, hosp in results:
            apps.append({
                "id": appt.id,
                "name": f"{doc_user.first_name} {doc_user.last_name}",
                "doctorId": doc_user.id,
                "date": appt.date,
                "time": appt.time_slot,
                "status": appt.status,
                "hospital": hosp.name
            })
            
    return jsonify(apps)

@app.route("/appointment/status", methods=["PUT"])
def update_appointment_status():
    data = request.json
    appt = Appointment.query.get(data['id'])
    
    if appt:
        appt.status = data['status']
        db.session.commit()
        
        # Get info for notification
        # We can fetch relationships easily now
        doctor = Doctor.query.get(appt.doctor_id)
        doc_user = User.query.get(doctor.user_id)
        patient_user = User.query.get(appt.patient_id)
        hospital = Hospital.query.get(appt.hospital_id)
        
        msg = f"Your appointment with Dr. {doc_user.first_name} {doc_user.last_name} at {hospital.name} on {appt.date} is {data['status'].lower()}."
        socketio.emit('notification', {'message': msg, 'email': patient_user.email})

        # Send Email on Confirmation
        if data['status'] == "Confirmed":
             email_details = {
                "doctor_name": f"{doc_user.first_name} {doc_user.last_name}",
                "doctor_email": doc_user.email,
                "hospital_name": hospital.name,
                "date": appt.date,
                "time": appt.time_slot,
                "lat": hospital.lat,
                "lng": hospital.lng
            }
             send_appointment_email(patient_user.email, email_details, status="Confirmed")
        
        elif data['status'] == "Rejected":
             email_details = {
                "doctor_name": f"{doc_user.first_name} {doc_user.last_name}",
                "doctor_email": doc_user.email,
                "hospital_name": hospital.name,
                "date": appt.date,
                "time": appt.time_slot
            }
             send_appointment_email(patient_user.email, email_details, status="Rejected")

        # Create notification record
        notif = Notification(user_id=patient_user.id, message=msg)
        db.session.add(notif)
        db.session.commit()

        return jsonify({"message": "Status updated"})
    return jsonify({"error": "Appointment not found"}), 404

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
        # Fetch user details if needed
        if (not patient_name or not gender) and email:
            u = User.query.filter_by(email=email).first()
            if u:
                if not patient_name:
                    patient_name = f"{u.first_name} {u.last_name}"
                if not gender:
                    gender = u.gender

        if not patient_name:
            patient_name = "Guest Patient"

        pdf_path = generate_pdf_report(patient_data, prediction, risk, summary, disease, patient_name, gender)
        
        # Save to History
        if email:
            u = User.query.filter_by(email=email).first()
            if u:
                date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                new_report = Report(
                    user_id=u.id,
                    disease_type=disease,
                    prediction=prediction,
                    risk_level=risk,
                    date=date_str,
                    pdf_path=pdf_path
                )
                db.session.add(new_report)
                db.session.commit()

        # Send Email Notification
        if email:
            print(f"📧 Sending report to {email}...")
            send_report_email(email, pdf_path, patient_name, disease)

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

    reports = Report.query.join(User).filter(User.email == email).order_by(Report.id.desc()).all()
    
    result = []
    for r in reports:
        result.append({
            "id": r.id,
            "disease_type": r.disease_type,
            "prediction": r.prediction,
            "risk_level": r.risk_level,
            "date": r.date,
            "pdf_path": r.pdf_path
        })
    return jsonify(result)

# ---------- PROFILE MANAGEMENT ----------
@app.route("/api/user/profile", methods=["GET", "PUT"])
def manage_profile():
    email = request.args.get("email")
    if not email and request.method == "PUT":
        email = request.json.get("email")
            
    if not email:
        return jsonify({"error": "Email required"}), 400

    user = User.query.filter_by(email=email).first()

    if request.method == "GET":
        if user:
            # Calculate Age if not set but DOB is present
            if not user.age and user.dob:
                try:
                    dob_date = datetime.datetime.strptime(user.dob, "%Y-%m-%d")
                    today = datetime.date.today()
                    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                    user.age = age
                    db.session.commit()
                except ValueError:
                    pass # Invalid Date Format

            return jsonify({
                 "firstName": user.first_name,
                 "lastName": user.last_name,
                 "email": user.email,
                 "phone": user.phone,
                 "dob": user.dob,
                 "city": user.city,
                 "pincode": user.pincode,
                 "address": user.address,
                 "age": user.age,
                 "weight": user.weight,
                 "height": user.height,
                 "profilePic": user.profile_pic,
                 "gender": user.gender
            })
        return jsonify({"error": "User not found"}), 404

    if request.method == "PUT":
        data = request.json
        if user:
            # Update fields
            user.first_name = data.get("firstName", user.first_name)
            user.last_name = data.get("lastName", user.last_name)
            user.dob = data.get("dob", user.dob)
            
            # Recalculate age if DOB changes
            if data.get("dob"):
                try:
                    dob_date = datetime.datetime.strptime(data.get("dob"), "%Y-%m-%d")
                    today = datetime.date.today()
                    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                    user.age = age
                except:
                    pass
            
            if data.get("age"):
                 user.age = data.get("age")

            user.gender = data.get("gender", user.gender)
            user.weight = data.get("weight", user.weight)
            user.height = data.get("height", user.height)
            user.address = data.get("address", user.address)
            user.city = data.get("city", user.city)
            user.pincode = data.get("pincode", user.pincode)
            if data.get("profilePic"):
                user.profile_pic = data.get("profilePic")
            
            db.session.commit()
            return jsonify({"message": "Profile updated successfully"})
        return jsonify({"error": "User not found"}), 404

# ---------- CHAT SYSTEM ----------
@app.route("/chat/history/<room_id>", methods=["GET"])
def get_chat_history(room_id):
    messages = Message.query.filter_by(room_id=room_id).order_by(Message.timestamp).all()
    history = []
    
    for msg in messages:
        if not msg.deleted_for_all:
             history.append({
                "id": msg.id,
                "senderId": msg.sender_id,
                "content": msg.content,
                "timestamp": msg.timestamp.strftime("%H:%M"),
                "isRead": msg.is_read,
                "isDeleted": msg.deleted_for_all
            })
    return jsonify(history)

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    sender_id = data['senderId']
    receiver_id = data['receiverId']
    content = data['content']
    
    # Save to DB
    new_msg = Message(
        room_id=room,
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content
    )
    db.session.add(new_msg)
    db.session.commit()
    
    msg_data = {
        "id": new_msg.id,
        "senderId": sender_id,
        "content": content,
        "timestamp": datetime.datetime.utcnow().strftime("%H:%M"),
        "isRead": False
    }
    
    emit('receive_message', msg_data, room=room)
    
    # Send Notification
    receiver = User.query.get(receiver_id)
    if receiver:
        sender_user = User.query.get(sender_id)
        if sender_user:
            notif_msg = f"New message from {sender_user.first_name}"
            
            # Save to DB
            new_notif = Notification(user_id=receiver.id, message=notif_msg)
            db.session.add(new_notif)
            db.session.commit()

            # Emit
            emit('notification', {'message': notif_msg, 'email': receiver.email}, broadcast=True)

@socketio.on('delete_message')
def delete_message(data):
    msg_id = data['id']
    msg = Message.query.get(msg_id)
    if msg:
        msg.deleted_for_all = True
        db.session.commit()
        emit('message_deleted', {'id': msg_id}, room=data['room'])

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)
