import sqlite3
import json
from werkzeug.security import generate_password_hash

# Tamil Nadu Major Cities Data
cities = {
    "Chennai": {"lat": 13.0827, "lng": 80.2707},
    "Coimbatore": {"lat": 11.0168, "lng": 76.9558},
    "Madurai": {"lat": 9.9252, "lng": 78.1198},
    "Trichy": {"lat": 10.7905, "lng": 78.7047},
    "Salem": {"lat": 11.6643, "lng": 78.1460},
    "Tirunelveli": {"lat": 8.7139, "lng": 77.7567},
    "Erode": {"lat": 11.3410, "lng": 77.7172},
    "Vellore": {"lat": 12.9165, "lng": 79.1325},
    "Thanjavur": {"lat": 10.7870, "lng": 79.1378},
    "Tuticorin": {"lat": 8.7642, "lng": 78.1348}
}

hospital_templates = [
    {"name": "Apollo Speciality Hospitals", "offset": (0.005, 0.005)},
    {"name": "Kavery Hospital", "offset": (-0.005, -0.005)},
    {"name": "Government Medical College Hospital", "offset": (0.01, -0.01)},
    {"name": "Vadamalayan Hospitals", "offset": (-0.01, 0.01)},
    {"name": "KMCH", "offset": (0.002, -0.008)}
]

doctor_names = [
    ("Dr. Senthil", "Kumar"), ("Dr. Priya", "Rajan"), ("Dr. Ravi", "Shankar"),
    ("Dr. Lakshmi", "Narayanan"), ("Dr. Anita", "Paul"), ("Dr. Abdul", "Kalam"),
    ("Dr. Meena", "Kumari"), ("Dr. Suresh", "Babu"), ("Dr. Karthik", "Raja"),
    ("Dr. Deepa", "Swaminathan"), ("Dr. Rajesh", "Kannan"), ("Dr. Malini", "Iyer")
]

specialties = [
    {"dept": "Cardiology", "role": "Senior Cardiologist", "exp": 15},
    {"dept": "Endocrinology", "role": "Diabetes Specialist", "exp": 12},
    {"dept": "General", "role": "General Physician", "exp": 8}
]

def seed_tn():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    print("Seeding Tamil Nadu Data...")

    count_hosp = 0
    count_doc = 0

    for city_name, coords in cities.items():
        base_lat = coords["lat"]
        base_lng = coords["lng"]
        
        # Add 2-3 hospitals per city
        for i, tmpl in enumerate(hospital_templates[:3]): 
            h_name = f"{tmpl['name']} - {city_name}"
            h_lat = base_lat + tmpl['offset'][0]
            h_lng = base_lng + tmpl['offset'][1]
            h_address = f"Main Road, {city_name}, Tamil Nadu"
            
            # Check overlap
            cursor.execute("SELECT id FROM hospitals WHERE name = ?", (h_name,))
            if cursor.fetchone():
                continue

            dept_json = json.dumps(["Cardiology", "Endocrinology", "General"])
            cursor.execute("INSERT INTO hospitals (name, address, lat, lng, departments) VALUES (?, ?, ?, ?, ?)",
                           (h_name, h_address, h_lat, h_lng, dept_json))
            h_id = cursor.lastrowid
            count_hosp += 1

            # Add doctors to this hospital
            for spec in specialties:
                # Pick a random name (cycling through list)
                doc_idx = (count_doc) % len(doctor_names)
                d_first, d_last = doctor_names[doc_idx]
                
                email = f"{d_first.lower()}.{d_last.lower()}.{count_doc}@tnhealth.com".replace(" ", "")
                
                # Check user
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                u_row = cursor.fetchone()
                
                if not u_row:
                    pw_hash = generate_password_hash("doctor123")
                    cursor.execute("""
                        INSERT INTO users (first_name, last_name, email, password, role, is_verified, city)
                        VALUES (?, ?, ?, ?, 'doctor', 1, ?)
                    """, (d_first, d_last, email, pw_hash, city_name))
                    u_id = cursor.lastrowid
                else:
                    u_id = u_row[0]

                # Add doctor profile
                avail = json.dumps(["09:00-11:00", "14:00-16:00", "17:00-19:00"])
                cursor.execute("""
                    INSERT INTO doctors (user_id, hospital_id, department, specialty, experience, availability)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (u_id, h_id, spec["dept"], spec["role"], spec["exp"], avail))
                count_doc += 1

    conn.commit()
    conn.close()
    print(f"✅ Successfully added {count_hosp} hospitals and {count_doc} doctors across Tamil Nadu.")

if __name__ == "__main__":
    seed_tn()
