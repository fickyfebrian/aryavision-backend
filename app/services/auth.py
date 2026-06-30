from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.auth import LoginRequest, TokenResponse
from app.repositories.admin import get_admin_by_username
from app.core.security import verify_password, create_access_token
from app.core.config import settings

def authenticate_admin(db: Session, login_data: LoginRequest) -> TokenResponse:
    admin = get_admin_by_username(db, login_data.username)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not verify_password(login_data.password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": str(admin.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )
