import os
import sys
from auth_db import create_users_table, create_otp_table, create_hospital_tables

def main():
    print("Initializing Database...")
    create_users_table()
    create_otp_table()
    create_hospital_tables()
    print("Database tables created/verified.")

if __name__ == "__main__":
    main()
