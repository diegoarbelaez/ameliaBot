"""
Slack Client for BotDO.
Handles Slack API interactions and webhook verification.
"""
import os
import hmac
import hashlib
import time
from typing import Optional
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackClient:
    """
    Client for interacting with Slack API.
    """
    
    def __init__(self):
        """
        Initialize Slack client with credentials from environment.
        """
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.signing_secret = os.getenv("SLACK_SIGNING_SECRET")
        
        if not self.bot_token:
            raise ValueError("SLACK_BOT_TOKEN not set in environment")
        if not self.signing_secret:
            raise ValueError("SLACK_SIGNING_SECRET not set in environment")
        
        self.client = WebClient(token=self.bot_token)
    
    def verify_slack_signature(
        self,
        timestamp: str,
        body: bytes,
        signature: str
    ) -> bool:
        """
        Verify that request came from Slack using signature verification.
        
        Args:
            timestamp: X-Slack-Request-Timestamp header value
            body: Raw request body as bytes
            signature: X-Slack-Signature header value
            
        Returns:
            True if signature is valid, False otherwise
        """
        # Check timestamp to prevent replay attacks
        # Request should be no older than 5 minutes
        if abs(time.time() - float(timestamp)) > 60 * 5:
            logger.warning("Slack request timestamp too old")
            return False
        
        # Compute the signature
        sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
        computed_signature = 'v0=' + hmac.new(
            self.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures using constant-time comparison
        return hmac.compare_digest(computed_signature, signature)
    
    def send_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None
    ) -> dict:
        """
        Send a message to a Slack channel.
        
        Args:
            channel: Slack channel ID
            text: Message text to send
            thread_ts: Thread timestamp for replies (optional)
            
        Returns:
            Slack API response
            
        Raises:
            SlackApiError: If sending fails
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts
            )
            return response
            
        except SlackApiError as e:
            logger.error(f"❌ Error enviando mensaje a Slack: {e.response['error']}")
            raise
    
    def get_user_info(self, user_id: str) -> dict:
        """
        Get information about a Slack user.
        
        Args:
            user_id: Slack user ID
            
        Returns:
            User information
            
        Raises:
            SlackApiError: If request fails
        """
        try:
            response = self.client.users_info(user=user_id)
            return response["user"]
        except SlackApiError as e:
            logger.error(f"❌ Error obteniendo info de usuario Slack")
            raise
    
    def get_channel_info(self, channel_id: str) -> dict:
        """
        Get information about a Slack channel.
        
        Args:
            channel_id: Slack channel ID
            
        Returns:
            Channel information
            
        Raises:
            SlackApiError: If request fails
        """
        try:
            # Try conversations.info first (works for all channel types)
            response = self.client.conversations_info(channel=channel_id)
            return response["channel"]
        except SlackApiError as e:
            logger.error(f"❌ Error obteniendo info de canal Slack")
            raise
    
    def remove_bot_mention(self, text: str, bot_user_id: Optional[str] = None) -> str:
        """
        Remove bot mention from message text.
        
        Args:
            text: Original message text
            bot_user_id: Bot's user ID (optional, will fetch if not provided)
            
        Returns:
            Text with bot mention removed
        """
        if not bot_user_id:
            # Get bot's own user ID
            try:
                auth_response = self.client.auth_test()
                bot_user_id = auth_response["user_id"]
            except SlackApiError:
                # If we can't get the bot ID, just return the original text
                return text.strip()
        
        # Remove mentions like <@U01234567>
        mention = f"<@{bot_user_id}>"
        cleaned_text = text.replace(mention, "").strip()
        
        return cleaned_text

