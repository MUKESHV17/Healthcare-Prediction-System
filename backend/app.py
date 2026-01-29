from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from auth_db import create_users_table, get_connection
import joblib
import numpy as np
import json
from otp_utils import generate_otp, otp_expiry
from auth_db import create_otp_table



app = Flask(__name__)
CORS(app)

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
        (first_name, last_name, dob, email, phone, city, pincode, password, is_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (first_name, last_name, dob, email, phone, city, pincode, password))

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
        "token": token
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
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not check_password_hash(user[0], password):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful"})


# ---------- DIABETES PREDICTION ----------
@app.route("/predict/diabetes", methods=["POST"])
def predict_diabetes():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    features = [
        data["Pregnancies"],
        data["Glucose"],
        data["BloodPressure"],
        data["SkinThickness"],
        data["Insulin"],
        data["BMI"],
        data["DiabetesPedigreeFunction"],
        data["Age"]
    ]

    input_data = np.array(features).reshape(1, -1)
    scaled_input = diabetes_scaler.transform(input_data)
    prediction = diabetes_model.predict(scaled_input)[0]

    return jsonify({
        "prediction": "Diabetic" if prediction == 1 else "Non-Diabetic"
    })


# ---------- HEART PREDICTION ----------
@app.route("/predict/heart", methods=["POST"])
def predict_heart():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    features = [data[feature] for feature in heart_features]
    input_data = np.array(features).reshape(1, -1)
    scaled_input = heart_scaler.transform(input_data)
    prediction = heart_model.predict(scaled_input)[0]

    return jsonify({
        "prediction": "Heart Disease Detected" if prediction == 1 else "No Heart Disease"
    })


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
