import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "users.db")

def update_schema():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # List of new columns to add
    new_columns = [
        ("address", "TEXT"),
        ("age", "INTEGER"),
        ("weight", "REAL"),
        ("height", "REAL"),
        ("profile_pic", "TEXT")
    ]
    
    for col_name, col_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f"Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column already exists: {col_name}")
            else:
                print(f"Error adding {col_name}: {e}")
                
    conn.commit()
    conn.close()
    print("Schema update completed.")

if __name__ == "__main__":
    update_schema()
