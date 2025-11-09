"""
Bot processing router for BotDO API.
Main endpoint for processing messages and generating AI responses.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from uuid import uuid4

from app.database import get_db
from app.schemas import BotProcessRequest, BotProcessResponse
from app.services.message_service import MessageService
from app.services.digitalocean_client import DigitalOceanClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bot", tags=["Bot"])


@router.post("/process", response_model=BotProcessResponse)
async def process_message(
    request: BotProcessRequest,
    db: Session = Depends(get_db)
):
    """
    Main bot processing endpoint.
    
    Flow:
    1. Save incoming user message to database
    2. Get conversation history (last 20 messages)
    3. Format conversation to OpenAI format
    4. Send to Digital Ocean Agent
    5. Save bot response to database
    6. Return bot response
    
    Args:
        request: Bot process request with message details
        db: Database session
        
    Returns:
        Bot process response with AI-generated reply
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        logger.info("=" * 60)
        logger.info("🤖 BOT PROCESS REQUEST - INICIO")
        logger.info(f"📊 Request info:")
        logger.info(f"   Plataforma: {request.platform}")
        logger.info(f"   Usuario: {request.user_name} (ID: {request.platform_user_id})")
        logger.info(f"   Canal: {request.channel_name} (ID: {request.platform_channel_id})")
        logger.info(f"   Mensaje: '{request.message_text}'")
        
        # Initialize services
        logger.info("🔧 Inicializando servicios...")
        message_service = MessageService(db)
        do_client = DigitalOceanClient()
        logger.info("✅ Servicios inicializados")
        
        # Step 1: Get or create user
        logger.info(f"👤 Obteniendo o creando usuario en BD...")
        user = message_service.get_or_create_user(
            platform=request.platform,
            platform_user_id=request.platform_user_id,
            display_name=request.user_name,
            email=request.user_email,
            platform_metadata=request.metadata
        )
        logger.info(f"✅ Usuario obtenido: DB ID={user.id}")
        
        # Step 2: Get or create channel
        logger.info(f"📺 Obteniendo o creando canal en BD...")
        channel = message_service.get_or_create_channel(
            platform=request.platform,
            channel_id=request.platform_channel_id,
            channel_name=request.channel_name,
            platform_metadata=request.metadata
        )
        logger.info(f"✅ Canal obtenido: DB ID={channel.id}")
        
        # Step 3: Save incoming user message
        logger.info(f"💾 Guardando mensaje del usuario en BD...")
        user_message = message_service.save_message(
            message_id=request.platform_message_id,
            channel=request.platform,
            direction="inbound",
            sender_type="user",
            message_text=request.message_text,
            timestamp=datetime.now(),
            user_id=user.id,
            channel_id=channel.id,
            platform_metadata=request.metadata
        )
        logger.info(f"✅ Mensaje guardado: DB ID={user_message.id}")
        
        # Step 4: Get conversation history (last 20 messages)
        logger.info(f"📚 Obteniendo historial de conversación (últimos 20 mensajes)...")
        conversation_history = message_service.get_conversation_history(
            channel_db_id=channel.id,
            limit=20
        )
        logger.info(f"✅ Historial obtenido: {len(conversation_history)} mensajes")
        
        # Step 5: Format to OpenAI format
        logger.info(f"🔄 Formateando mensajes a formato OpenAI...")
        openai_messages = message_service.format_to_openai(conversation_history)
        
        # Include the current message if not already in history
        if not any(msg.get("content") == request.message_text for msg in openai_messages):
            openai_messages.append({
                "role": "user",
                "content": request.message_text
            })
            logger.info(f"➕ Mensaje actual agregado al contexto")
        
        logger.info(f"✅ Total de mensajes en contexto: {len(openai_messages)}")
        
        # Step 6: Send to Digital Ocean Agent
        logger.info(f"🌊 Enviando conversación a Digital Ocean Agent...")
        bot_response_text = await do_client.send_to_agent(
            messages=openai_messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        logger.info(f"✅ Respuesta recibida de Digital Ocean Agent ({len(bot_response_text)} chars)")
        
        # Step 7: Save bot response
        logger.info(f"💾 Guardando respuesta del bot en BD...")
        bot_message_id = f"{request.platform}_bot_{uuid4()}"
        bot_message = message_service.save_message(
            message_id=bot_message_id,
            channel=request.platform,
            direction="outbound",
            sender_type="bot",
            message_text=bot_response_text,
            timestamp=datetime.now(),
            user_id=None,  # Bot messages don't have a user
            channel_id=channel.id,
            platform_metadata={
                "in_reply_to": request.platform_message_id,
                **request.metadata
            }
        )
        
        logger.info(f"✅ Respuesta guardada: DB ID={bot_message.id}")
        
        # Step 8: Return response
        logger.info("🎉 BOT PROCESS REQUEST - COMPLETADO EXITOSAMENTE")
        logger.info("=" * 60)
        
        return BotProcessResponse(
            success=True,
            bot_response=bot_response_text,
            message_id=bot_message.id
        )
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ ERROR PROCESANDO MENSAJE:")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Tipo: {type(e).__name__}")
        logger.error("=" * 60, exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/health")
async def bot_health_check():
    """
    Health check for bot service.
    
    Returns:
        Status of bot service and Digital Ocean Agent connection
    """
    try:
        do_client = DigitalOceanClient()
        agent_available = await do_client.health_check()
        
        return {
            "status": "healthy" if agent_available else "degraded",
            "bot_service": "running",
            "digitalocean_agent": "connected" if agent_available else "unavailable"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "bot_service": "running",
            "digitalocean_agent": "error",
            "error": str(e)
        }

