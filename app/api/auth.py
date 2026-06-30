from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database.connection import get_db
from app.schemas.auth import AdminResponse, LoginRequest, TokenResponse
from app.services.auth import authenticate_admin
from app.api.deps import get_current_admin
from app.models.admin import Admin
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", summary="Login Admin")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint.
    Note: To support Swagger UI's "Authorize" button natively, this endpoint 
    accepts `application/x-www-form-urlencoded` (OAuth2PasswordRequestForm).
    """
    # Mapping form data to LoginRequest schema
    login_req = LoginRequest(username=form_data.username, password=form_data.password)
    
    token_response = authenticate_admin(db, login_req)
    
    return success_response(
        data={
            "access_token": token_response.access_token,
            "token_type": token_response.token_type
        },
        message="Login successful"
    )

@router.post("/login/json", summary="Login Admin (JSON Body)", include_in_schema=False)
async def login_json(
    login_req: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Alternative login endpoint that strictly accepts JSON body.
    """
    token_response = authenticate_admin(db, login_req)
    return success_response(
        data={
            "access_token": token_response.access_token,
            "token_type": token_response.token_type
        },
        message="Login successful"
    )

@router.get("/me", response_model=None, summary="Get Current Admin")
async def get_me(current_admin: Admin = Depends(get_current_admin)):
    """
    Mengembalikan data admin yang sedang login.
    Membutuhkan Authorization header dengan Bearer token.
    """
    return success_response(
        data={
            "id": current_admin.id,
            "username": current_admin.username
        },
        message="Admin profile retrieved successfully"
    )
