"""
Pydantic schemas for request/response validation in BotDO API.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


# ============================================
# Authentication Schemas
# ============================================

class Token(BaseModel):
    """Response schema for login endpoint"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data"""
    username: Optional[str] = None


class AdminUserCreate(BaseModel):
    """Schema for creating a new admin user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Ensure username is alphanumeric"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (can include _ and -)')
        return v


class AdminUserResponse(BaseModel):
    """Schema for admin user response"""
    id: UUID
    username: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str
    password: str


# ============================================
# User Schemas (Message Senders)
# ============================================

class UserBase(BaseModel):
    """Base schema for user"""
    platform: str = Field(..., description="Platform: slack, whatsapp, web")
    platform_user_id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    display_name: Optional[str] = None
    email: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# Channel Schemas
# ============================================

class ChannelBase(BaseModel):
    """Base schema for channel"""
    platform: str = Field(..., description="Platform: slack, whatsapp, web")
    channel_id: str
    channel_name: Optional[str] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None


class ChannelCreate(ChannelBase):
    """Schema for creating a new channel"""
    pass


class ChannelUpdate(BaseModel):
    """Schema for updating a channel"""
    channel_name: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ChannelResponse(ChannelBase):
    """Schema for channel response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# Message Schemas
# ============================================

class MessageBase(BaseModel):
    """Base schema for message"""
    message_id: str
    channel: str = Field(..., description="Origin: slack, whatsapp, web")
    direction: str = Field(..., description="Direction: inbound, outbound")
    sender_type: str = Field(..., description="Sender type: bot, user")
    message_text: Optional[str] = None
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('channel')
    def validate_channel(cls, v):
        """Validate channel value"""
        allowed = ['slack', 'whatsapp', 'web']
        if v not in allowed:
            raise ValueError(f'Channel must be one of: {", ".join(allowed)}')
        return v
    
    @validator('direction')
    def validate_direction(cls, v):
        """Validate direction value"""
        allowed = ['inbound', 'outbound']
        if v not in allowed:
            raise ValueError(f'Direction must be one of: {", ".join(allowed)}')
        return v
    
    @validator('sender_type')
    def validate_sender_type(cls, v):
        """Validate sender_type value"""
        allowed = ['bot', 'user']
        if v not in allowed:
            raise ValueError(f'Sender type must be one of: {", ".join(allowed)}')
        return v


class MessageCreate(MessageBase):
    """Schema for creating a new message"""
    user_id: Optional[UUID] = None
    channel_id: Optional[UUID] = None


class MessageUpdate(BaseModel):
    """Schema for updating a message"""
    message_text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(MessageBase):
    """Schema for message response"""
    id: UUID
    user_id: Optional[UUID] = None
    channel_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# List/Filter Schemas
# ============================================

class MessageFilter(BaseModel):
    """Schema for filtering messages"""
    channel: Optional[str] = None
    direction: Optional[str] = None
    sender_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class UserFilter(BaseModel):
    """Schema for filtering users"""
    platform: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# ============================================
# Bot Processing Schemas
# ============================================

class BotProcessRequest(BaseModel):
    """Schema for bot processing request"""
    platform: str = Field(..., description="Platform: slack, whatsapp, web")
    platform_message_id: str = Field(..., description="Message ID from the platform")
    platform_channel_id: str = Field(..., description="Channel ID from the platform")
    platform_user_id: str = Field(..., description="User ID from the platform")
    message_text: str = Field(..., description="Content of the message")
    user_name: Optional[str] = Field(None, description="User's display name")
    channel_name: Optional[str] = Field(None, description="Channel's display name")
    user_email: Optional[str] = Field(None, description="User's email")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Platform-specific metadata")
    
    @validator('platform')
    def validate_platform(cls, v):
        """Validate platform value"""
        allowed = ['slack', 'whatsapp', 'web']
        if v not in allowed:
            raise ValueError(f'Platform must be one of: {", ".join(allowed)}')
        return v


class BotProcessResponse(BaseModel):
    """Schema for bot processing response"""
    success: bool = Field(..., description="Whether the request was processed successfully")
    bot_response: str = Field(..., description="Bot's response text")
    message_id: UUID = Field(..., description="UUID of the saved bot message")
    error: Optional[str] = Field(None, description="Error message if processing failed")


class ConversationMessage(BaseModel):
    """Schema for OpenAI-format conversation message"""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    
    @validator('role')
    def validate_role(cls, v):
        """Validate role value"""
        allowed = ['user', 'assistant', 'system']
        if v not in allowed:
            raise ValueError(f'Role must be one of: {", ".join(allowed)}')
        return v


# ============================================
# Slack Event Schemas
# ============================================

class SlackEventAppMention(BaseModel):
    """Schema for Slack app_mention event"""
    type: str
    user: str
    text: str
    ts: str
    channel: str
    event_ts: str


class SlackEventRequest(BaseModel):
    """Schema for Slack Event API request"""
    token: Optional[str] = None
    team_id: Optional[str] = None
    api_app_id: Optional[str] = None
    event: Optional[Dict[str, Any]] = None
    type: str
    event_id: Optional[str] = None
    event_time: Optional[int] = None
    challenge: Optional[str] = None  # For URL verification


class SlackMessageRequest(BaseModel):
    """Schema for sending messages to Slack"""
    channel: str = Field(..., description="Slack channel ID")
    text: str = Field(..., description="Message text to send")
    thread_ts: Optional[str] = Field(None, description="Thread timestamp for replies")

