"""
User CRUD routes for BotDO API.
Handles operations for tracking message senders across platforms.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import AdminUser, User
from app.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
def list_users(
    platform: Optional[str] = Query(None, description="Filter by platform (slack, whatsapp, web)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """
    List users with optional filters.
    Requires authentication.
    
    Args:
        platform: Filter by platform
        limit: Maximum number of users to return
        offset: Number of users to skip (for pagination)
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of users matching the filters
    """
    query = db.query(User)
    
    # Apply platform filter
    if platform:
        query = query.filter(User.platform == platform)
    
    # Order by created_at descending (most recent first)
    query = query.order_by(User.created_at.desc())
    
    # Apply pagination
    users = query.offset(offset).limit(limit).all()
    
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Create a new user.
    Requires authentication.
    
    Args:
        user_data: User data to create
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If user with same platform and platform_user_id already exists
    """
    # Check if user already exists for this platform
    existing_user = db.query(User).filter(
        User.platform == user_data.platform,
        User.platform_user_id == user_data.platform_user_id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with platform_user_id '{user_data.platform_user_id}' "
                   f"already exists for platform '{user_data.platform}'"
        )
    
    # Create new user
    db_user = User(**user_data.model_dump())
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )
    
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Get a specific user by ID.
    Requires authentication.
    
    Args:
        user_id: UUID of the user
        db: Database session
        current_user: Authenticated user
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Update a user.
    Requires authentication.
    
    Args:
        user_id: UUID of the user to update
        user_data: Updated user data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated user
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )
    
    # Update only provided fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update user: {str(e)}"
        )
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Delete a user.
    Requires authentication.
    
    Args:
        user_id: UUID of the user to delete
        db: Database session
        current_user: Authenticated user
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )
    
    db.delete(user)
    db.commit()
    
    return None

