import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "users.db")

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            dob TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            city TEXT,
            pincode TEXT,
            password TEXT,
            role TEXT DEFAULT 'patient',
            address TEXT,
            age INTEGER,
            weight REAL,
            height REAL,
            profile_pic TEXT,
            is_verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_hospital_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Hospitals Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            lat REAL,
            lng REAL,
            departments TEXT  -- JSON string of departments
        )
    """)

    # Doctors Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            hospital_id INTEGER,
            department TEXT,
            specialty TEXT,
            experience INTEGER,
            availability TEXT, -- JSON string of slots
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (hospital_id) REFERENCES hospitals (id)
        )
    """)

    # Appointments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            hospital_id INTEGER,
            date TEXT,
            time_slot TEXT,
            status TEXT DEFAULT 'Pending Confirmation',
            FOREIGN KEY (patient_id) REFERENCES users (id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (id),
            FOREIGN KEY (hospital_id) REFERENCES hospitals (id)
        )
    """)

    # Notifications Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()

def create_otp_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            otp TEXT,
            expires_at INTEGER
        )
    """)

    conn.commit()
    conn.close()
