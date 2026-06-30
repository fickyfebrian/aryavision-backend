from sqlalchemy.orm import Session
from app.models.admin import Admin
from app.core.security import get_password_hash

def get_admin_by_username(db: Session, username: str) -> Admin | None:
    return db.query(Admin).filter(Admin.username == username).first()

def get_admin_by_id(db: Session, admin_id: int) -> Admin | None:
    return db.query(Admin).filter(Admin.id == admin_id).first()

def create_admin(db: Session, username: str, plain_password: str) -> Admin:
    hashed_password = get_password_hash(plain_password)
    db_admin = Admin(username=username, password=hashed_password)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin
