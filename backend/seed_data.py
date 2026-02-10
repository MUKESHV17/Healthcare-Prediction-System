from flask import Flask
from models import db, User, Hospital, Doctor, Appointment
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
import random

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///users.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Real Hospital Data (Tamil Nadu & Major Cities)
hospitals_data = [
    # Chennai
    {"name": "Apollo Main Hospital", "address": "Greams Road, Chennai", "lat": 13.0634, "lng": 80.2555},
    {"name": "Fortis Malar Hospital", "address": "Adyar, Chennai", "lat": 13.0039, "lng": 80.2543},
    {"name": "MIOT International", "address": "Manapakkam, Chennai", "lat": 13.0232, "lng": 80.1874},
    {"name": "Sri Ramachandra Medical Centre", "address": "Porur, Chennai", "lat": 13.0336, "lng": 80.1610},
    {"name": "Global Health City", "address": "Perumbakkam, Chennai", "lat": 12.8984, "lng": 80.2315},
    
    # Madurai
    {"name": "Meenakshi Mission Hospital", "address": "Melur Road, Madurai", "lat": 9.9252, "lng": 78.1482},
    {"name": "Apollo Speciality Hospitals", "address": "Lake View Road, Madurai", "lat": 9.9328, "lng": 78.1402},
    {"name": "Velammal Medical College Hospital", "address": "Anuppanadi, Madurai", "lat": 9.8970, "lng": 78.1470},
    {"name": "Vadamalayan Hospitals", "address": "Chokkikulam, Madurai", "lat": 9.9304, "lng": 78.1325},
    
    # Coimbatore
    {"name": "G. Kuppuswamy Naidu Memorial Hospital", "address": "Pappanaickenpalayam, Coimbatore", "lat": 11.0142, "lng": 76.9806},
    {"name": "PSG Hospitals", "address": "Peelamedu, Coimbatore", "lat": 11.0267, "lng": 77.0270},
    {"name": "KMCH (Kovai Medical Center)", "address": "Avinashi Road, Coimbatore", "lat": 11.0396, "lng": 77.0433},
    
    # Bangalore
    {"name": "Manipal Hospital", "address": "Old Airport Road, Bangalore", "lat": 12.9555, "lng": 77.6534},
    {"name": "Sakra World Hospital", "address": "Marathahalli, Bangalore", "lat": 12.9324, "lng": 77.6848},
    
    # Mumbai
    {"name": "Lilavati Hospital", "address": "Bandra West, Mumbai", "lat": 19.0506, "lng": 72.8286},
    {"name": "Kokilaben Dhirubhai Ambani Hospital", "address": "Andheri West, Mumbai", "lat": 19.1311, "lng": 72.8251},
    
    # Trichy
    {"name": "Kauvery Hospital", "address": "Tennur, Trichy", "lat": 10.8229, "lng": 78.6854},
    {"name": "Apollo Speciality Hospitals", "address": "Thillai Nagar, Trichy", "lat": 10.8305, "lng": 78.6824},
    
    # Salem
    {"name": "Manipal Hospitals", "address": "Dalmia Board, Salem", "lat": 11.6643, "lng": 78.1460},
    {"name": "SKS Hospital", "address": "Fairlands, Salem", "lat": 11.6853, "lng": 78.1492},
    
    # Tirunelveli
    {"name": "Galaxy Hospital", "address": "Vannarpettai, Tirunelveli", "lat": 8.7139, "lng": 77.7567},
    {"name": "Tirunelveli Medical College Hospital", "address": "Palayamkottai, Tirunelveli", "lat": 8.7166, "lng": 77.7470},

    # Other Major TN
    {"name": "Christian Medical College (CMC)", "address": "Vellore", "lat": 12.9246, "lng": 79.1333},
    {"name": "Aravind Eye Hospital", "address": "Anna Nagar, Madurai", "lat": 9.9275, "lng": 78.1384},
    
    # Delhi
    {"name": "AIIMS New Delhi", "address": "Ansari Nagar, New Delhi", "lat": 28.5672, "lng": 77.2100},
    {"name": "Sir Ganga Ram Hospital", "address": "Rajinder Nagar, New Delhi", "lat": 28.6387, "lng": 77.1950},
]

departments = [
    "Cardiology", "Endocrinology", "General", "Pediatrics", "Neurology", "Orthopedics"
]

default_availability = [
    {"day": "Monday", "slots": ["09:00 AM - 11:00 AM", "04:00 PM - 06:00 PM"]},
    {"day": "Tuesday", "slots": ["09:00 AM - 11:00 AM", "04:00 PM - 06:00 PM"]},
    {"day": "Wednesday", "slots": ["10:00 AM - 01:00 PM"]},
    {"day": "Thursday", "slots": ["09:00 AM - 11:00 AM", "04:00 PM - 06:00 PM"]},
    {"day": "Friday", "slots": ["10:00 AM - 01:00 PM"]},
     {"day": "Saturday", "slots": ["10:00 AM - 01:00 PM"]}
]

def seed_data():
    with app.app_context():
        print("Clearing existing Hospital and Doctor data (Users retained if possible, else cleaned)...")
        # Optional: Clear tables to avoid duplicates. 
        # CAREFUL: This deletes data. Since user asked to "update 2025 real map", a clean slate for hospitals is best.
        # We will NOT delete patients, but we will delete doctor-users to recreate them cleanly.
        
        db.session.query(Appointment).delete()
        db.session.query(Doctor).delete()
        db.session.query(Hospital).delete()
        
        # Delete users with role 'doctor' to avoid duplicates
        db.session.query(User).filter_by(role='doctor').delete()
        
        db.session.commit()
        print("Old data cleared.")

        print("Seeding Hospitals...")
        hospital_objs = []
        for h_data in hospitals_data:
            h = Hospital(
                name=h_data["name"],
                address=h_data["address"],
                lat=h_data["lat"],
                lng=h_data["lng"],
                departments=departments # Assign all departments to these major hospitals
            )
            db.session.add(h)
            hospital_objs.append(h)
        
        db.session.commit() # Commit to get IDs
        
        print(f"Created {len(hospital_objs)} hospitals.")

        print("Seeding Doctors...")
        # Create 5-6 doctors per hospital
        
        doc_names = [
            ("Rajesh", "Kumar"), ("Sita", "Lakshmi"), ("Arun", "Vijay"), ("Priya", "Menon"), 
            ("Suresh", "Raina"), ("Deepa", "Mehta"), ("Karthik", "Subbaraj"), ("Anita", "Desai"),
            ("Manoj", "Tiwari"), ("Meera", "Jasmine"), ("Ravi", "Shastri"), ("Sneha", "Ullal")
        ]
        
        count = 0
        for h in hospital_objs:
            # Add doctors for different departments
            for i, dept in enumerate(departments):
                # Cycle through names
                fname, lname = doc_names[(i + h.id) % len(doc_names)]
                
                # Create User for Doctor
                email = f"{fname.lower()}.{lname.lower()}{h.id}{i}@hospital.com"
                
                # Check if exists (shouldn't due to delete above, but safety)
                if not User.query.filter_by(email=email).first():
                    user = User(
                        first_name=fname,
                        last_name=lname,
                        email=email,
                        password=generate_password_hash("password123"),
                        role="doctor",
                        phone=f"9876543{h.id}{i}",
                        city=h.address.split(",")[-1].strip(),
                        gender="Male" if i % 2 == 0 else "Female"
                    )
                    db.session.add(user)
                    db.session.commit()
                    
                    # Create Doctor Profile
                    doctor = Doctor(
                        user_id=user.id,
                        hospital_id=h.id,
                        department=dept,
                        specialty=f"Senior {dept} Specialist",
                        experience=5 + (i * 2),
                        availability=random.sample(default_availability, k=random.randint(3, 6))
                    )
                    db.session.add(doctor)
                    count += 1
        
        db.session.commit()
        print(f"Successfully created {count} doctors.")
        print("Seeding Complete!")

if __name__ == "__main__":
    seed_data()
