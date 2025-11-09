"""
Message Service for BotDO.
Handles message storage, retrieval, and conversation formatting for AI models.
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID

from app.models import Message, User, Channel
from app.schemas import MessageCreate


class MessageService:
    """
    Service for managing messages, users, and channels across platforms.
    """
    
    def __init__(self, db: Session):
        """
        Initialize message service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_or_create_user(
        self,
        platform: str,
        platform_user_id: str,
        display_name: Optional[str] = None,
        email: Optional[str] = None,
        platform_metadata: Optional[Dict[str, Any]] = None
    ) -> User:
        """
        Get existing user or create new one.
        
        Args:
            platform: Platform name (slack, whatsapp, web)
            platform_user_id: User ID from the platform
            display_name: User's display name
            email: User's email
            platform_metadata: Additional platform-specific metadata
            
        Returns:
            User object
        """
        # Try to find existing user
        user = self.db.query(User).filter(
            User.platform == platform,
            User.platform_user_id == platform_user_id
        ).first()
        
        if user:
            # Update user info if provided
            if display_name and display_name != user.display_name:
                user.display_name = display_name
            if email and email != user.email:
                user.email = email
            if platform_metadata:
                user.platform_metadata = platform_metadata
            self.db.commit()
            self.db.refresh(user)
            return user
        
        # Create new user
        new_user = User(
            platform=platform,
            platform_user_id=platform_user_id,
            display_name=display_name,
            email=email,
            platform_metadata=platform_metadata
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        return new_user
    
    def get_or_create_channel(
        self,
        platform: str,
        channel_id: str,
        channel_name: Optional[str] = None,
        platform_metadata: Optional[Dict[str, Any]] = None
    ) -> Channel:
        """
        Get existing channel or create new one.
        
        Args:
            platform: Platform name (slack, whatsapp, web)
            channel_id: Channel ID from the platform
            channel_name: Channel's display name
            platform_metadata: Additional platform-specific metadata
            
        Returns:
            Channel object
        """
        # Try to find existing channel
        channel = self.db.query(Channel).filter(
            Channel.platform == platform,
            Channel.channel_id == channel_id
        ).first()
        
        if channel:
            # Update channel info if provided
            if channel_name and channel_name != channel.channel_name:
                channel.channel_name = channel_name
            if platform_metadata:
                channel.platform_metadata = platform_metadata
            self.db.commit()
            self.db.refresh(channel)
            return channel
        
        # Create new channel
        new_channel = Channel(
            platform=platform,
            channel_id=channel_id,
            channel_name=channel_name,
            is_active=True,
            platform_metadata=platform_metadata
        )
        self.db.add(new_channel)
        self.db.commit()
        self.db.refresh(new_channel)
        
        return new_channel
    
    def save_message(
        self,
        message_id: str,
        channel: str,
        direction: str,
        sender_type: str,
        message_text: str,
        timestamp: datetime,
        user_id: Optional[UUID] = None,
        channel_id: Optional[UUID] = None,
        platform_metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Save a message to the database.
        
        Args:
            message_id: Unique message ID from platform
            channel: Platform name (slack, whatsapp, web)
            direction: Message direction (inbound, outbound)
            sender_type: Sender type (bot, user)
            message_text: Content of the message
            timestamp: Original message timestamp
            user_id: UUID of the user (optional)
            channel_id: UUID of the channel (optional)
            platform_metadata: Additional platform-specific data
            
        Returns:
            Created Message object
        """
        # Check if message already exists
        existing = self.db.query(Message).filter(
            Message.message_id == message_id
        ).first()
        
        if existing:
            return existing
        
        # Create new message
        new_message = Message(
            message_id=message_id,
            channel=channel,
            direction=direction,
            sender_type=sender_type,
            user_id=user_id,
            channel_id=channel_id,
            message_text=message_text,
            timestamp=timestamp,
            platform_metadata=platform_metadata
        )
        
        self.db.add(new_message)
        self.db.commit()
        self.db.refresh(new_message)
        
        return new_message
    
    def get_conversation_history(
        self,
        channel_db_id: UUID,
        limit: int = 20
    ) -> List[Message]:
        """
        Get conversation history for a channel.
        
        Args:
            channel_db_id: Database UUID of the channel
            limit: Maximum number of messages to retrieve (default: 20)
            
        Returns:
            List of Message objects ordered by timestamp (oldest first)
        """
        messages = self.db.query(Message).filter(
            Message.channel_id == channel_db_id
        ).order_by(
            Message.timestamp.asc()
        ).limit(limit).all()
        
        return messages
    
    def format_to_openai(self, messages: List[Message]) -> List[Dict[str, str]]:
        """
        Format messages to OpenAI chat format.
        
        Args:
            messages: List of Message objects
            
        Returns:
            List of messages in OpenAI format:
            [
                {"role": "user", "content": "message text"},
                {"role": "assistant", "content": "response text"},
                ...
            ]
        """
        openai_messages = []
        
        for msg in messages:
            # Determine role based on sender_type
            role = "assistant" if msg.sender_type == "bot" else "user"
            
            # Only include messages with text
            if msg.message_text:
                openai_messages.append({
                    "role": role,
                    "content": msg.message_text
                })
        
        return openai_messages
    
    def get_channel_by_platform_id(
        self,
        platform: str,
        platform_channel_id: str
    ) -> Optional[Channel]:
        """
        Get channel by platform and platform channel ID.
        
        Args:
            platform: Platform name
            platform_channel_id: Channel ID from the platform
            
        Returns:
            Channel object or None
        """
        return self.db.query(Channel).filter(
            Channel.platform == platform,
            Channel.channel_id == platform_channel_id
        ).first()

