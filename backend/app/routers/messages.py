"""
Message CRUD routes for BotDO API.
Handles operations for the unified messages table across all platforms.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models import AdminUser, Message
from app.schemas import (
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    MessageFilter
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/messages", tags=["Messages"])


@router.get("/", response_model=List[MessageResponse])
def list_messages(
    channel: Optional[str] = Query(None, description="Filter by channel (slack, whatsapp, web)"),
    direction: Optional[str] = Query(None, description="Filter by direction (inbound, outbound)"),
    sender_type: Optional[str] = Query(None, description="Filter by sender type (bot, user)"),
    date_from: Optional[datetime] = Query(None, description="Filter messages from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter messages until this date"),
    limit: int = Query(100, ge=1, le=1000, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """
    List messages with optional filters.
    Requires authentication.
    
    Args:
        channel: Filter by channel origin
        direction: Filter by message direction
        sender_type: Filter by sender type
        date_from: Start date for filtering
        date_to: End date for filtering
        limit: Maximum number of messages to return
        offset: Number of messages to skip (for pagination)
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of messages matching the filters
    """
    query = db.query(Message)
    
    # Apply filters
    if channel:
        query = query.filter(Message.channel == channel)
    
    if direction:
        query = query.filter(Message.direction == direction)
    
    if sender_type:
        query = query.filter(Message.sender_type == sender_type)
    
    if date_from:
        query = query.filter(Message.timestamp >= date_from)
    
    if date_to:
        query = query.filter(Message.timestamp <= date_to)
    
    # Order by timestamp descending (most recent first)
    query = query.order_by(Message.timestamp.desc())
    
    # Apply pagination
    messages = query.offset(offset).limit(limit).all()
    
    return messages


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Create a new message.
    Requires authentication.
    
    Args:
        message_data: Message data to create
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created message
        
    Raises:
        HTTPException: If message_id already exists
    """
    # Check if message_id already exists
    existing_message = db.query(Message).filter(
        Message.message_id == message_data.message_id
    ).first()
    
    if existing_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message with ID '{message_data.message_id}' already exists"
        )
    
    # Create new message
    db_message = Message(**message_data.model_dump())
    
    try:
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create message: {str(e)}"
        )
    
    return db_message


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Get a specific message by ID.
    Requires authentication.
    
    Args:
        message_id: UUID of the message
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Message data
        
    Raises:
        HTTPException: If message not found
    """
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID '{message_id}' not found"
        )
    
    return message


@router.put("/{message_id}", response_model=MessageResponse)
def update_message(
    message_id: UUID,
    message_data: MessageUpdate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Update a message.
    Requires authentication.
    
    Args:
        message_id: UUID of the message to update
        message_data: Updated message data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated message
        
    Raises:
        HTTPException: If message not found
    """
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID '{message_id}' not found"
        )
    
    # Update only provided fields
    update_data = message_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(message, field, value)
    
    try:
        db.commit()
        db.refresh(message)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update message: {str(e)}"
        )
    
    return message


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Delete a message.
    Requires authentication.
    
    Args:
        message_id: UUID of the message to delete
        db: Database session
        current_user: Authenticated user
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: If message not found
    """
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID '{message_id}' not found"
        )
    
    db.delete(message)
    db.commit()
    
    return None

