"""
WhatsApp/Whapi connector for BotDO API.
Handles Whapi webhook events and message sending.

TODO: Implement Whapi integration following the same pattern as Slack connector.
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
import logging

from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/canales/whapi", tags=["Whapi Connector"])


@router.post("/events")
async def whapi_events(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Receive webhook events from Whapi.
    
    TODO: Implement Whapi event handling
    - Verify webhook signature
    - Parse incoming messages
    - Call bot processing endpoint
    - Send response back via Whapi API
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Response to Whapi
    """
    logger.info("Whapi events endpoint called (not yet implemented)")
    return {"status": "not_implemented"}


@router.post("/send")
async def send_whapi_message(
    request: Request
):
    """
    Send a message via Whapi (for manual/admin use).
    
    TODO: Implement message sending via Whapi API
    
    Args:
        request: Message details
        
    Returns:
        Whapi API response
    """
    logger.info("Whapi send endpoint called (not yet implemented)")
    return {"status": "not_implemented"}


@router.get("/health")
async def whapi_health():
    """
    Health check for Whapi connector.
    
    Returns:
        Status of Whapi integration
    """
    return {
        "status": "not_implemented",
        "connected": False,
        "message": "Whapi integration not yet implemented"
    }

