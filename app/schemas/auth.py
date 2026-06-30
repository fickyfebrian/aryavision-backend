from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class AdminResponse(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True
