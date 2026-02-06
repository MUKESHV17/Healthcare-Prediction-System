import sqlite3
import json
import random
from werkzeug.security import generate_password_hash

# Categories requested
DEPARTMENTS = ["Cardiology", "Endocrinology", "Neurology", "Orthopedics", "General", "Pediatrics"]

# Locations with approx lat/lng
LOCATIONS = [
    # Chennai
    {"name": "Govt General Hospital", "city": "Chennai", "area": "Central", "pincode": "600001", "lat": 13.0827, "lng": 80.2707},
    {"name": "Apollo Hospitals Greams Road", "city": "Chennai", "area": "Thousand Lights", "pincode": "600006", "lat": 13.0650, "lng": 80.2550},
    {"name": "Bloom Healthcare", "city": "Chennai", "area": "T. Nagar", "pincode": "600035", "lat": 13.0418, "lng": 80.2341},
    {"name": "Anna Nagar Multi-Specialty", "city": "Chennai", "area": "Anna Nagar", "pincode": "600021", "lat": 13.0850, "lng": 80.2100},

    # Madurai
    {"name": "Madurai City Hospital", "city": "Madurai", "area": "City Centre", "pincode": "625001", "lat": 9.9252, "lng": 78.1198},
    {"name": "Apollo Speciality Madurai", "city": "Madurai", "area": "K.K. Nagar", "pincode": "625020", "lat": 9.9390, "lng": 78.1410},
    {"name": "Meenakshi Mission Hospital", "city": "Madurai", "area": "Melur Road", "pincode": "625107", "lat": 9.9530, "lng": 78.1630},
    {"name": "Vadamalayan Hospitals", "city": "Madurai", "area": "Chokkikulam", "pincode": "625002", "lat": 9.9350, "lng": 78.1300},

    # Coimbatore
    {"name": "Coimbatore Govt Hospital", "city": "Coimbatore", "area": "Central", "pincode": "641001", "lat": 11.0168, "lng": 76.9558},
    {"name": "PSG Hospitals", "city": "Coimbatore", "area": "Peelamedu", "pincode": "641004", "lat": 11.0300, "lng": 77.0300},
    {"name": "KMCH (Kovai Medical)", "city": "Coimbatore", "area": "Avinashi Road", "pincode": "641014", "lat": 11.0500, "lng": 77.0600},

    # Trichy
    {"name": "Trichy Govt Hospital", "city": "Trichy", "area": "Cantonment", "pincode": "620001", "lat": 10.7905, "lng": 78.7047},
    {"name": "Trichy Medical Centre", "city": "Trichy", "area": "Thillai Nagar", "pincode": "620017", "lat": 10.8200, "lng": 78.6900},
    
    # Hyderabad
    {"name": "Care Hospitals", "city": "Hyderabad", "area": "Banjara Hills", "pincode": "500034", "lat": 17.4130, "lng": 78.4350},
    {"name": "Apollo Jubilee Hills", "city": "Hyderabad", "area": "Jubilee Hills", "pincode": "500033", "lat": 17.4300, "lng": 78.4100},
    {"name": "KIMS Hospitals", "city": "Hyderabad", "area": "Secunderabad", "pincode": "500003", "lat": 17.4400, "lng": 78.5000},
    {"name": "Yashoda Hospitals", "city": "Hyderabad", "area": "Somajiguda", "pincode": "500082", "lat": 17.4250, "lng": 78.4500},

    # Mumbai
    {"name": "Bombay Hospital", "city": "Mumbai", "area": "Marine Lines", "pincode": "400020", "lat": 18.9400, "lng": 72.8250},
    {"name": "KEM Hospital", "city": "Mumbai", "area": "Parel", "pincode": "400012", "lat": 19.0020, "lng": 72.8410},
    {"name": "Kokilaben Dhirubhai Ambani Hospital", "city": "Mumbai", "area": "Andheri West", "pincode": "400053", "lat": 19.1300, "lng": 72.8200},

    # Delhi
    {"name": "AIIMS Delhi", "city": "Delhi", "area": "Ansari Nagar", "pincode": "110029", "lat": 28.5672, "lng": 77.2100},
    {"name": "Max Super Speciality", "city": "Delhi", "area": "Saket", "pincode": "110017", "lat": 28.5200, "lng": 77.2200},
    {"name": "Fortis Hospital", "city": "Delhi", "area": "Shalimar Bagh", "pincode": "110088", "lat": 28.7100, "lng": 77.1500},
]

FIRST_NAMES = ["Dr. Rajesh", "Dr. Amit", "Dr. Priya", "Dr. Sneha", "Dr. Abdul", "Dr. Sarah", "Dr. John", "Dr. Karthik", "Dr. Anjali", "Dr. Vikram", "Dr. Meera", "Dr. Suresh", "Dr. Ramesh", "Dr. Deepa", "Dr. Arjun", "Dr. Sanjay", "Dr. Neha", "Dr. Pooja", "Dr. Vijay", "Dr. Lakshmi"]
LAST_NAMES = ["Kumar", "Sharma", "Reddy", "Patel", "Singh", "Iyer", "Nair", "Rao", "Gupta", "Verma", "Mehta", "Chopra", "Das", "Babu", "Rajan"]

def seed_mega_data():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    print("Clearing old hospital & doctor data...")
    cursor.execute("DELETE FROM doctors")
    cursor.execute("DELETE FROM hospitals")
    cursor.execute("DELETE FROM users WHERE role = 'doctor'")
    
    print("Seeding Mega Data...")
    
    hp_count = 0
    doc_count = 0
    password_hash = generate_password_hash("doctor123")

    for loc in LOCATIONS:
        # Create Hospital
        depts_json = json.dumps(DEPARTMENTS)
        address = f"{loc['area']}, {loc['city']}, Pincode: {loc['pincode']}"
        
        cursor.execute("INSERT INTO hospitals (name, address, lat, lng, departments) VALUES (?, ?, ?, ?, ?)",
                       (loc['name'], address, loc['lat'], loc['lng'], depts_json))
        h_id = cursor.lastrowid
        hp_count += 1
        
        # Add 10 Doctors per hospital
        for i in range(10):
            f_name = random.choice(FIRST_NAMES)
            l_name = random.choice(LAST_NAMES)
            email = f"{f_name.lower()}.{l_name.lower()}.{random.randint(1000,9999)}@care.com".replace(" ", "").replace("dr.", "dr.")
            
            # Create User
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, password, role, is_verified, city, pincode)
                VALUES (?, ?, ?, ?, 'doctor', 1, ?, ?)
            """, (f_name, l_name, email, password_hash, loc['city'], loc['pincode']))
            u_id = cursor.lastrowid
            
            # Assign Dept & Specialty
            dept = DEPARTMENTS[i % len(DEPARTMENTS)] # Distribute evenly
            specialty = f"Senior {dept} Specialist"
            exp = random.randint(5, 30)
            
            # Random Availability
            slots = []
            if random.choice([True, False]): slots.append("09:00-11:00")
            if random.choice([True, False]): slots.append("11:00-13:00")
            if random.choice([True, False]): slots.append("14:00-16:00")
            if random.choice([True, False]): slots.append("17:00-19:00")
            if not slots: slots.append("10:00-12:00") # Ensure at least one
            
            cursor.execute("""
                INSERT INTO doctors (user_id, hospital_id, department, specialty, experience, availability)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (u_id, h_id, dept, specialty, exp, json.dumps(slots)))
            doc_count += 1
            
    conn.commit()
    conn.close()
    print(f"✅ Mega Seed Complete: {hp_count} Hospitals, {doc_count} Doctors.")

if __name__ == "__main__":
    seed_mega_data()
