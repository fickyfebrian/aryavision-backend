import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.repositories.admin import create_admin, get_admin_by_username

def seed_admin():
    db: Session = SessionLocal()
    try:
        username = "admin"
        password = "admin123"
        
        existing_admin = get_admin_by_username(db, username)
        if existing_admin:
            print(f"Admin '{username}' already exists.")
            return
            
        create_admin(db, username=username, plain_password=password)
        print(f"Admin '{username}' created successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
