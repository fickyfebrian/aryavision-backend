from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.config import settings
from app.database.connection import get_db
from app.models.admin import Admin
from app.repositories.admin import get_admin_by_id

# We use tokenUrl="api/auth/login" so Swagger UI knows where to send credentials
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    secret_key = getattr(settings, "SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    algorithm = "HS256"
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        admin_id_str: str = payload.get("sub")
        if admin_id_str is None:
            raise credentials_exception
        admin_id = int(admin_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
        
    admin = get_admin_by_id(db, admin_id=admin_id)
    if admin is None:
        raise credentials_exception
        
    return admin
