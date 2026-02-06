import sqlite3
import json

def add_krishnagiri_hospital():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Krishnagiri coordinates (approx based on pincode 635001)
    lat = 12.5266
    lng = 78.2146
    
    # Check if already exists to avoid duplicates
    cursor.execute("SELECT id FROM hospitals WHERE name = 'Krishnagiri Multi-Specialty'")
    if cursor.fetchone():
        print("Hospital already exists.")
        conn.close()
        return

    # Insert Hospital
    cursor.execute("""
        INSERT INTO hospitals (name, address, lat, lng, departments)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "Krishnagiri Multi-Specialty", 
        "45/A, Gandhi Road, Krishnagiri", 
        lat, 
        lng, 
        json.dumps(["Cardiology", "Endocrinology", "General", "Pediatrics"])
    ))
    
    hospital_id = cursor.lastrowid
    print(f"Added Hospital ID: {hospital_id}")

    # Add a Doctor to this hospital
    # We need a user account for the doctor first
    cursor.execute("SELECT id FROM users WHERE email = 'dr.krish@hospital.com'")
    user_row = cursor.fetchone()
    
    if not user_row:
        # Create user for doctor
        from werkzeug.security import generate_password_hash
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, password, role, is_verified)
            VALUES (?, ?, ?, ?, ?, 1)
        """, ("Dr. Krish", "Kumar", "dr.krish@hospital.com", generate_password_hash("doctor123"), "doctor"))
        user_id = cursor.lastrowid
    else:
        user_id = user_row[0]

    # Add doctor entry
    cursor.execute("""
        INSERT INTO doctors (user_id, hospital_id, department, specialty, experience, availability)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id, 
        hospital_id, 
        "Cardiology", 
        "Chief Cardiologist", 
        20, 
        json.dumps(["10:00-11:00", "14:00-16:00", "18:00-20:00"])
    ))
    
    # Add another doctor
    cursor.execute("""
        INSERT INTO doctors (user_id, hospital_id, department, specialty, experience, availability)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id, # Reusing same user for demo simplicity, or create new one. Let's reuse.
        hospital_id, 
        "Endocrinology", 
        "Diabetes Specialist", 
        12, 
        json.dumps(["09:00-12:00", "16:00-18:00"])
    ))

    conn.commit()
    conn.close()
    print("Successfully added Krishnagiri hospital and doctors.")

if __name__ == "__main__":
    add_krishnagiri_hospital()
