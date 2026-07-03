import sys
from pathlib import Path
import logging

# Ensure the app module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import SessionLocal
from app.repositories.admin import get_admin_by_username, create_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_admins():
    db = SessionLocal()
    try:
        admins_to_seed = [
            {"username": "admin", "password": "admin123"},
            {"username": "ficky", "password": "ficky123"}
        ]
        
        for admin_data in admins_to_seed:
            username = admin_data["username"]
            existing_admin = get_admin_by_username(db, username)
            
            if existing_admin:
                logger.info(f"Admin '{username}' already exists. Skipping.")
            else:
                create_admin(db, username=username, plain_password=admin_data["password"])
                logger.info(f"Admin '{username}' created successfully.")
                
    except Exception as e:
        logger.error(f"Error seeding admins: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admins()
