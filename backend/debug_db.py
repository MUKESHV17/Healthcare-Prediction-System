from flask import Flask
from models import db, User, Doctor, Appointment, Hospital
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///users.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def debug_data():
    with app.app_context():
        print("--- Debugging Data ---")
        
        # 1. list all doctors with their emails
        print("\n1. All Doctors:")
        doctors = Doctor.query.all()
        for d in doctors:
            u = User.query.get(d.user_id)
            print(f"Dr. {u.first_name} {u.last_name} (ID: {d.id}) - Email: {u.email}")
            
        # 2. List all appointments
        print("\n2. All Appointments:")
        appts = Appointment.query.all()
        for a in appts:
            doc = Doctor.query.get(a.doctor_id)
            doc_user = User.query.get(doc.user_id)
            pat_user = User.query.get(a.patient_id)
            print(f"Appt ID: {a.id} | Patient: {pat_user.email} -> Dr: {doc_user.email} (DocID: {doc.id}) | Status: {a.status}")

if __name__ == "__main__":
    debug_data()
