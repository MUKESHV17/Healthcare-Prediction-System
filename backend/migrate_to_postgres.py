import sqlite3
import os
from flask import Flask
from models import db, User, Hospital, Doctor, Appointment, Notification, Report, OTP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SQLITE_DB_PATH = 'users.db'
POSTGRES_DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def migrate_users(cursor):
    print("Migrating Users...")
    cursor.execute("SELECT * FROM users")
    columns = [description[0] for description in cursor.description]
    
    for row in cursor.fetchall():
        data = dict(zip(columns, row))
        
        # Handle case where column might not exist in old DB or new Model has default
        user = User(
            id=data.get('id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            dob=data.get('dob'),
            email=data.get('email'),
            phone=data.get('phone'),
            city=data.get('city'),
            pincode=data.get('pincode'),
            password=data.get('password'),
            role=data.get('role', 'patient'),
            address=data.get('address'),
            age=data.get('age'),
            weight=data.get('weight'),
            height=data.get('height'),
            profile_pic=data.get('profile_pic'),
            is_verified=data.get('is_verified', 0),
            gender=data.get('gender', 'Male')
        )
        db.session.add(user)
        # Adjust sequence if needed later, but explicitly setting ID usually works
    db.session.commit()

def migrate_hospitals(cursor):
    print("Migrating Hospitals...")
    cursor.execute("SELECT * FROM hospitals")
    columns = [description[0] for description in cursor.description]

    for row in cursor.fetchall():
        data = dict(zip(columns, row))
        hospital = Hospital(
            id=data.get('id'),
            name=data.get('name'),
            address=data.get('address'),
            lat=data.get('lat'),
            lng=data.get('lng'),
            _departments=data.get('departments') # Raw JSON string
        )
        db.session.add(hospital)
    db.session.commit()

def migrate_doctors(cursor):
    print("Migrating Doctors...")
    cursor.execute("SELECT * FROM doctors")
    columns = [description[0] for description in cursor.description]

    for row in cursor.fetchall():
        data = dict(zip(columns, row))
        doctor = Doctor(
            id=data.get('id'),
            user_id=data.get('user_id'),
            hospital_id=data.get('hospital_id'),
            department=data.get('department'),
            specialty=data.get('specialty'),
            experience=data.get('experience'),
            _availability=data.get('availability')
        )
        db.session.add(doctor)
    db.session.commit()

def migrate_appointments(cursor):
    print("Migrating Appointments...")
    cursor.execute("SELECT * FROM appointments")
    columns = [description[0] for description in cursor.description]

    for row in cursor.fetchall():
        data = dict(zip(columns, row))
        appointment = Appointment(
            id=data.get('id'),
            patient_id=data.get('patient_id'),
            doctor_id=data.get('doctor_id'),
            hospital_id=data.get('hospital_id'),
            date=data.get('date'),
            time_slot=data.get('time_slot'),
            status=data.get('status', 'Pending Confirmation')
        )
        db.session.add(appointment)
    db.session.commit()

def migrate_reports(cursor):
    print("Migrating Reports...")
    try:
        cursor.execute("SELECT * FROM reports")
        columns = [description[0] for description in cursor.description]
        
        for row in cursor.fetchall():
            data = dict(zip(columns, row))
            report = Report(
                id=data.get('id'),
                user_id=data.get('user_id'),
                disease_type=data.get('disease_type'),
                prediction=data.get('prediction'),
                risk_level=data.get('risk_level'),
                date=data.get('date'),
                pdf_path=data.get('pdf_path')
            )
            db.session.add(report)
        db.session.commit()
    except sqlite3.OperationalError:
        print("Reports table not found in SQLite, skipping.")

def main():
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"Error: {SQLITE_DB_PATH} not found.")
        return

    print("Connecting to SQLite...")
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_cursor = sqlite_conn.cursor()

    print("Creating PostgreSQL tables...")
    with app.app_context():
        db.create_all()

        # Migrate Data
        try:
            migrate_users(sqlite_cursor)
            migrate_hospitals(sqlite_cursor)
            migrate_doctors(sqlite_cursor)
            migrate_appointments(sqlite_cursor)
            migrate_reports(sqlite_cursor)
            
            # Reset sequences (Important for Postgres SERIAL)
            # This is a bit hacky but ensuring next inserts don't fail
            for table in ['users', 'hospitals', 'doctors', 'appointments', 'reports']:
                try:
                    db.session.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), coalesce(max(id),0) + 1, false) FROM {table};")
                except Exception as e:
                    print(f"Sequence reset warning for {table}: {e}")
            
            db.session.commit()
            print("Migration completed successfully!")
        except Exception as e:
            print(f"Migration failed: {e}")
            db.session.rollback()
        finally:
            sqlite_conn.close()

if __name__ == "__main__":
    main()
