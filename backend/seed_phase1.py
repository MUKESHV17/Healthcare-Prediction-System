import sqlite3
import json
import random
from werkzeug.security import generate_password_hash

# ----------------- CONFIGURATION -----------------

# Cities Data (Lat/Lng are approximate centers)
CITIES = {
    "Chennai": {"lat": 13.0827, "lng": 80.2707, "hospitals": [
        {"name": "Apollo Main", "area": "Greams Road", "pincode": "600006"},
        {"name": "Fortis Malar", "area": "Adyar", "pincode": "600020"},
        {"name": "MIOT International", "area": "Manapakkam", "pincode": "600089"},
        {"name": "Sims Hospital", "area": "Vadapalani", "pincode": "600026"},
        {"name": "Kauvery Hospital", "area": "Alwarpet", "pincode": "600018"}
    ]},
    "Madurai": {"lat": 9.9252, "lng": 78.1198, "hospitals": [
        {"name": "Apollo Speciality", "area": "K.K. Nagar", "pincode": "625020"},
        {"name": "Meenakshi Mission", "area": "Melur Road", "pincode": "625107"},
        {"name": "Vadamalayan Hospitals", "area": "Chokkikulam", "pincode": "625002"},
        {"name": "Velammal Medical", "area": "Ring Road", "pincode": "625009"},
        {"name": "Hannah Joseph Hospital", "area": "Bye Pass Road", "pincode": "625016"}
    ]},
    "Coimbatore": {"lat": 11.0168, "lng": 76.9558, "hospitals": [
        {"name": "PSG Hospitals", "area": "Peelamedu", "pincode": "641004"},
        {"name": "KMCH Main", "area": "Avinashi Road", "pincode": "641014"},
        {"name": "Ganga Hospital", "area": "Mettupalayam Road", "pincode": "641043"},
        {"name": "G. Kuppuswamy Naidu", "area": "Pappanaickenpalayam", "pincode": "641037"},
        {"name": "Sri Ramakrishna", "area": "Siddhapudur", "pincode": "641044"}
    ]},
    "Trichy": {"lat": 10.7905, "lng": 78.7047, "hospitals": [
        {"name": "Kauvery Heart City", "area": "Cantonment", "pincode": "620001"},
        {"name": "Apollo Speciality", "area": "Thillai Nagar", "pincode": "620018"},
        {"name": "Trichy SRM Medical", "area": "Irungalur", "pincode": "621105"},
        {"name": "Maruti Hospital", "area": "Tennur", "pincode": "620017"}
    ]},
    "Hyderabad": {"lat": 17.3850, "lng": 78.4867, "hospitals": [
        {"name": "Apollo Jubilee Hills", "area": "Jubilee Hills", "pincode": "500033"},
        {"name": "Care Hospitals", "area": "Banjara Hills", "pincode": "500034"},
        {"name": "Yashoda Hospitals", "area": "Somajiguda", "pincode": "500082"},
        {"name": "KIMS", "area": "Secunderabad", "pincode": "500003"},
        {"name": "Sunshine Hospitals", "area": "Paradise", "pincode": "500003"}
    ]},
    "Mumbai": {"lat": 19.0760, "lng": 72.8777, "hospitals": [
        {"name": "Lilavati Hospital", "area": "Bandra West", "pincode": "400050"},
        {"name": "Kokilaben Dhirubhai", "area": "Andheri West", "pincode": "400053"},
        {"name": "Nanavati Max", "area": "Vile Parle", "pincode": "400056"},
        {"name": "Hinduja Hospital", "area": "Mahim", "pincode": "400016"},
        {"name": "Bombay Hospital", "area": "Marine Lines", "pincode": "400020"}
    ]},
    "Delhi": {"lat": 28.7041, "lng": 77.1025, "hospitals": [
        {"name": "AIIMS", "area": "Ansari Nagar", "pincode": "110029"},
        {"name": "Apollo Indraprastha", "area": "Sarita Vihar", "pincode": "110076"},
        {"name": "Max Super Speciality", "area": "Saket", "pincode": "110017"},
        {"name": "Fortis Escorts", "area": "Okhla Road", "pincode": "110025"},
        {"name": "Sir Ganga Ram", "area": "Rajinder Nagar", "pincode": "110060"}
    ]}
}

# Doctor Roles Distribution (Total 10 per hospital)
DOCTOR_DISTRIBUTION = [
    {"dept": "Endocrinology", "count": 3, "role": "Diabetologist"},
    {"dept": "Cardiology", "count": 3, "role": "Cardiologist"},
    {"dept": "General", "count": 1, "role": "General Physician"},
    {"dept": "Pediatrics", "count": 1, "role": "Pediatrician"},
    {"dept": "Orthopedics", "count": 1, "role": "Orthopedic Surgeon"},
    {"dept": "Neurology", "count": 1, "role": "Neurologist"}
]

# Random Names
FIRST_NAMES = ["Dr. Rajesh", "Dr. Priya", "Dr. Senthil", "Dr. Amit", "Dr. Sneha", "Dr. Karthik", "Dr. Lakshmi", "Dr. Ravi", "Dr. Meera", "Dr. Vijay", "Dr. Anjali", "Dr. Vikram", "Dr. Divya", "Dr. Rahul", "Dr. Nithya", "Dr. Sanjay", "Dr. Kavitha", "Dr. Suresh", "Dr. Malini", "Dr. Arvind"]
LAST_NAMES = ["Kumar", "Rajan", "Sharma", "Reddy", "Iyer", "Nair", "Patel", "Singh", "Rao", "Gupta", "Verma", "Menon", "Krishnan", "Balaji", "Ganesh"]

# Availability Logic
DAYS_OFFERED = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

def generate_slots():
    # Generate 4-6 days per week
    num_days = random.randint(4, 6)
    days = random.sample(DAYS_OFFERED, num_days)
    
    # Generate slots 9am-6pm (30 mins)
    # Simplified: Pick 3-5 random hour blocks for demo display
    # Real logic would be more complex time objects, here we store string ranges for UI
    
    possible_slots = [
        "09:00-09:30", "09:30-10:00", "10:00-10:30", "10:30-11:00",
        "11:00-11:30", "11:30-12:00", "14:00-14:30", "14:30-15:00",
        "15:00-15:30", "15:30-16:00", "16:00-16:30", "16:30-17:00",
        "17:00-17:30", "17:30-18:00"
    ]
    
    # Pick 5-8 random slots per doctor to show availability
    return random.sample(possible_slots, random.randint(5, 8))

def seed_phase1():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    print("🧹 Cleaning existing data...")
    cursor.execute("DELETE FROM doctors")
    cursor.execute("DELETE FROM hospitals")
    cursor.execute("DELETE FROM users WHERE role = 'doctor'")
    
    print("🌱 Seeding Phase 1 Data...")
    
    password_hash = generate_password_hash("doctor123")
    
    total_hospitals = 0
    total_doctors = 0
    
    for city, data in CITIES.items():
        base_lat = data["lat"]
        base_lng = data["lng"]
        
        for hosp in data["hospitals"]:
            # Generate slightly offset coordinates for realism within city
            # offset roughly 0.01 to 0.05 degrees (~1-5km)
            lat_offset = random.uniform(-0.05, 0.05)
            lng_offset = random.uniform(-0.05, 0.05)
            
            h_lat = base_lat + lat_offset
            h_lng = base_lng + lng_offset
            
            address = f"{hosp['area']}, {city}, {hosp['pincode']}"
            all_depts = [d["dept"] for d in DOCTOR_DISTRIBUTION]
            
            cursor.execute("""
                INSERT INTO hospitals (name, address, lat, lng, departments)
                VALUES (?, ?, ?, ?, ?)
            """, (hosp["name"], address, h_lat, h_lng, json.dumps(all_depts)))
            
            hospital_id = cursor.lastrowid
            total_hospitals += 1
            
            # --- Generate 10 Doctors per Hospital ---
            for dist in DOCTOR_DISTRIBUTION:
                count = dist["count"]
                dept = dist["dept"]
                role_title = dist["role"]
                
                for _ in range(count):
                    f_name = random.choice(FIRST_NAMES)
                    l_name = random.choice(LAST_NAMES)
                    # Unique email
                    # Ensure no spaces and lowercase
                    clean_fname = f_name.lower().replace(" ", "").replace("dr.", "dr.")
                    clean_lname = l_name.lower().replace(" ", "")
                    email = f"{clean_fname}.{clean_lname}.{random.randint(10000,99999)}@hms.com"
                    
                    # Create User
                    cursor.execute("""
                        INSERT INTO users (first_name, last_name, email, password, role, is_verified, city, pincode)
                        VALUES (?, ?, ?, ?, 'doctor', 1, ?, ?)
                    """, (f_name, l_name, email, password_hash, city, hosp['pincode']))
                    user_id = cursor.lastrowid
                    
                    # Specialty nuances
                    exp = random.randint(3, 25)
                    slots = generate_slots()
                    
                    cursor.execute("""
                        INSERT INTO doctors (user_id, hospital_id, department, specialty, experience, availability)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, hospital_id, dept, role_title, exp, json.dumps(slots)))
                    
                    total_doctors += 1

    conn.commit()
    conn.close()
    print(f"✅ Phase 1 Seed Complete!")
    print(f"🏥 Hospitals Created: {total_hospitals}")
    print(f"👨‍⚕️ Doctors Created: {total_doctors}")

if __name__ == "__main__":
    seed_phase1()
