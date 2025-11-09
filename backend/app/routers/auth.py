"""
Authentication routes for BotDO API.
Handles user registration, login, and token management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import AdminUser
from app.schemas import (
    AdminUserCreate,
    AdminUserResponse,
    LoginRequest,
    Token
)
from app.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: AdminUserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new admin user.
    
    Args:
        user_data: User registration data (username, email, password)
        db: Database session
        
    Returns:
        Created admin user data
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    existing_user = db.query(AdminUser).filter(
        AdminUser.username == user_data.username
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(AdminUser).filter(
        AdminUser.email == user_data.email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new admin user
    hashed_password = get_password_hash(user_data.password)
    
    db_user = AdminUser(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    return db_user


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with username and password.
    
    Args:
        login_data: Login credentials (username, password)
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=AdminUserResponse)
def get_me(
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    Requires Bearer token in Authorization header.
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        Current user data
    """
    return current_user

