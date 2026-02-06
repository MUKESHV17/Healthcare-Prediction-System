import sqlite3
import os
import json
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "users.db")

def seed_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Add Hospitals
    hospitals = [
        ("City Central Hospital", "123 Main St, Mumbai", 19.0760, 72.8777, json.dumps(["Cardiology", "Endocrinology", "General"])),
        ("Green Valley Clinic", "456 Park Rd, Bangalore", 12.9716, 77.5946, json.dumps(["Endocrinology", "Dermatology"])),
        ("Heart Care Institute", "789 Skyline Ave, Delhi", 28.6139, 77.2090, json.dumps(["Cardiology", "Surgery"]))
    ]
    
    cursor.executemany("INSERT INTO hospitals (name, address, lat, lng, departments) VALUES (?, ?, ?, ?, ?)", hospitals)
    print("Seeded Hospitals.")

    # 2. Add some Demo Doctors (as users first)
    # Note: These are placeholder passwords
    doctor_users = [
        ("Dr. John", "Smith", "1980-01-01", "john.smith@hospital.com", "9999999901", "Mumbai", "400001", generate_password_hash("doctor123"), "doctor"),
        ("Dr. Sarah", "Connor", "1985-05-05", "sarah.c@hospital.com", "9999999902", "Bangalore", "560001", generate_password_hash("doctor123"), "doctor")
    ]
    
    for doc in doctor_users:
        try:
            cursor.execute("""
                INSERT INTO users (first_name, last_name, dob, email, phone, city, pincode, password, role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, doc)
        except sqlite3.IntegrityError:
            print(f"User {doc[3]} already exists.")

    conn.commit()

    # Link Doctors to Hospitals
    cursor.execute("SELECT id FROM users WHERE role = 'doctor'")
    doc_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM hospitals")
    hosp_ids = [row[0] for row in cursor.fetchall()]

    if len(doc_ids) >= 2 and len(hosp_ids) >= 2:
        doctors_meta = [
            (doc_ids[0], hosp_ids[0], "Cardiology", "Senior Cardiologist", 15, json.dumps(["10:00-10:30", "11:00-11:30", "14:00-14:30"])),
            (doc_ids[1], hosp_ids[1], "Endocrinology", "Diabetes Specialist", 10, json.dumps(["09:00-09:30", "10:00-10:30", "15:00-15:30"]))
        ]
        cursor.executemany("""
            INSERT INTO doctors (user_id, hospital_id, department, specialty, experience, availability)
            VALUES (?, ?, ?, ?, ?, ?)
        """, doctors_meta)
        print("Seeded Doctors.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_data()
