from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import database
import os
from datetime import datetime, timedelta
import hashlib
import secrets
from typing import Optional
from jose import jwt
from config import settings

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    user_id: str
    name: str
    role: str
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str
    user_id: str


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def hash_password(password: str) -> str:
    """Hash a password using SHA256 with salt"""
    salt = os.urandom(16).hex()
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 100000)
    return f"{salt}${hash_obj.hex()}"


def verify_password(password: str, hash_str: str) -> bool:
    """Verify a password against its hash"""
    try:
        salt, hash_hex = hash_str.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 100000)
        return hash_obj.hex() == hash_hex
    except:
        return False


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    User login endpoint
    """
    try:
        if database.db is None:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        # Find user by username
        user = await database.db.users.find_one({"username": request.username})
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get password hash
        pwd_hash = user["password_hash"]
        
        # Verify password
        verified = verify_password(request.password, pwd_hash)
        
        if not verified:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user["username"], "role": user["role"]}
        )
        
        # Update last login
        try:
            await database.db.users.update_one(
                {"username": request.username},
                {"$set": {"last_login": datetime.utcnow()}}
            )
        except:
            pass
        
        return LoginResponse(
            success=True,
            user_id=user["user_id"],
            name=user["name"],
            role=user["role"],
            message=f"Welcome back, {user['name']}!",
            access_token=access_token,
            token_type="bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login
    """
    user = await database.db.users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user["role"],
        "name": user["name"],
        "user_id": user["user_id"]
    }


@router.post("/logout")
async def logout():
    """Logout endpoint (client-side session clearing)"""
    return {"success": True, "message": "Logged out successfully"}


@router.get("/test-users")
async def get_test_users():
    """Get all test user credentials (for development only)"""
    return {
        "students": [
            {"username": "2024001", "password": "student123", "name": "Rajesh Kumar"},
            {"username": "2024002", "password": "student123", "name": "Priya Singh"},
            {"username": "2024003", "password": "student123", "name": "Amit Patel"},
        ],
        "teachers": [
            {"username": "teacher01", "password": "teacher123", "name": "Dr. Sharma"},
            {"username": "teacher02", "password": "teacher123", "name": "Prof. Desai"},
        ],
        "admin": [
            {"username": "admin", "password": "admin123", "name": "System Admin"},
        ]
    }
