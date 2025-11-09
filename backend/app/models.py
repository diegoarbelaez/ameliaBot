"""
SQLAlchemy ORM models for BotDO database.
"""
from sqlalchemy import Column, String, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class AdminUser(Base):
    """
    Admin users for API authentication.
    """
    __tablename__ = "admin_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class User(Base):
    """
    Track message senders across platforms.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(String(50), nullable=False, index=True)  # 'slack', 'whatsapp', 'web'
    platform_user_id = Column(String(255), nullable=False)  # User ID from the platform
    display_name = Column(String(255), index=True)
    email = Column(String(255))
    platform_metadata = Column(JSONB)  # Additional platform-specific data
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    messages = relationship("Message", back_populates="user")

    def __repr__(self):
        return f"<User {self.display_name} ({self.platform})>"


class Channel(Base):
    """
    Communication channels across platforms.
    """
    __tablename__ = "channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(String(50), nullable=False, index=True)  # 'slack', 'whatsapp', 'web'
    channel_id = Column(String(255), nullable=False)  # Channel ID from the platform
    channel_name = Column(String(255))
    is_active = Column(Boolean, default=True, index=True)
    platform_metadata = Column(JSONB)  # Additional platform-specific data
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    messages = relationship("Message", back_populates="channel_ref")

    def __repr__(self):
        return f"<Channel {self.channel_name} ({self.platform})>"


class Message(Base):
    """
    Unified message storage for all channels.
    Main table for storing all messages across platforms.
    """
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(String(255), unique=True, nullable=False)  # Message ID from the platform
    channel = Column(String(50), nullable=False, index=True)  # Origin: 'slack', 'whatsapp', 'web'
    direction = Column(String(20), nullable=False, index=True)  # 'inbound' or 'outbound'
    sender_type = Column(String(20), nullable=False, index=True)  # 'bot' or 'user'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), index=True)
    channel_id = Column(UUID(as_uuid=True), ForeignKey('channels.id', ondelete='SET NULL'), index=True)
    message_text = Column(Text)
    timestamp = Column(TIMESTAMP, nullable=False, index=True)  # Original message timestamp
    platform_metadata = Column(JSONB)  # Platform-specific data (thread_ts, message_type, etc.)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="messages")
    channel_ref = relationship("Channel", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.message_id} from {self.channel} ({self.direction})>"

