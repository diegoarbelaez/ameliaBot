"""
Slack connector for BotDO API.
Handles Slack event subscriptions and message sending.
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any
import time
from collections import OrderedDict
import asyncio

from app.database import get_db
from app.schemas import SlackEventRequest, SlackMessageRequest, BotProcessRequest
from app.services.slack_client import SlackClient
from app.routers.bot import process_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/canales/slack", tags=["Slack Connector"])

# Event deduplication cache
# Key: event_id, Value: timestamp when processed
_processed_events: OrderedDict[str, float] = OrderedDict()
_MAX_CACHE_SIZE = 1000  # Maximum events to keep in cache
_CACHE_TTL = 3600  # 1 hour in seconds


def _is_event_processed(event_id: str) -> bool:
    """
    Check if an event has already been processed.
    Cleans up old entries from cache.
    
    Args:
        event_id: Unique event identifier
        
    Returns:
        True if event was already processed, False otherwise
    """
    current_time = time.time()
    
    # Clean up old entries (older than TTL)
    keys_to_remove = []
    for key, timestamp in _processed_events.items():
        if current_time - timestamp > _CACHE_TTL:
            keys_to_remove.append(key)
        else:
            break  # OrderedDict, so once we hit a recent one, rest are recent
    
    for key in keys_to_remove:
        del _processed_events[key]
    
    # Check if event already processed
    if event_id in _processed_events:
        logger.warning(f"⚠️  Evento duplicado detectado: {event_id}")
        return True
    
    # Mark as processed
    _processed_events[event_id] = current_time
    
    # Limit cache size
    while len(_processed_events) > _MAX_CACHE_SIZE:
        _processed_events.popitem(last=False)  # Remove oldest
    
    return False


async def _process_app_mention_background(
    event: Dict[str, Any],
    event_id: str
):
    """
    Process app_mention in background with error handling.
    Creates its own DB session since the original one from the request is closed.
    
    Args:
        event: Slack event data
        event_id: Unique event identifier for logging
    """
    from app.database import SessionLocal
    
    db = SessionLocal()
    slack_client = SlackClient()
    
    try:
        logger.info(f"🔄 Background task iniciada para evento: {event_id}")
        await handle_app_mention(event, slack_client, db)
        logger.info(f"✅ Background task completada para evento: {event_id}")
    except Exception as e:
        logger.error(f"❌ Error en background processing de evento {event_id}: {str(e)}", exc_info=True)
    finally:
        db.close()


@router.post("/events")
async def slack_events(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Receive events from Slack Event API.
    
    Handles:
    - URL verification challenge
    - app_mention events (when bot is mentioned)
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Response based on event type
    """
    try:
        logger.info("=" * 60)
        logger.info("📨 NUEVO EVENTO DE SLACK RECIBIDO")
        
        # Get raw body for signature verification
        body = await request.body()
        
        # Get Slack signature headers
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        signature = request.headers.get("X-Slack-Signature", "")
        
        logger.info(f"🔐 Verificando firma de Slack (timestamp: {timestamp})")
        
        # Initialize Slack client
        slack_client = SlackClient()
        
        # Verify the request came from Slack
        if not slack_client.verify_slack_signature(timestamp, body, signature):
            logger.error("❌ Firma de Slack inválida - REQUEST RECHAZADO")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        logger.info("✅ Firma de Slack verificada correctamente")
        
        # Parse the event payload
        event_data = await request.json()
        event_type_main = event_data.get("type")
        
        logger.info(f"📋 Tipo de evento principal: {event_type_main}")
        
        # Handle URL verification challenge
        if event_type_main == "url_verification":
            challenge = event_data.get("challenge")
            logger.info(f"🔐 Slack URL verification challenge recibido: {challenge[:20]}...")
            return {"challenge": challenge}
        
        # Handle event callbacks
        if event_type_main == "event_callback":
            event = event_data.get("event", {})
            event_type = event.get("type")
            
            logger.info(f"📨 Event callback recibido - tipo: {event_type}")
            logger.info(f"📝 Datos del evento: {event}")
            
            # Handle app_mention events (bot is mentioned with @)
            if event_type == "app_mention":
                user_id = event.get('user')
                channel_id = event.get('channel')
                text = event.get('text', '')
                event_ts = event.get('event_ts', '')
                client_msg_id = event.get('client_msg_id', '')
                
                # Create unique event ID for deduplication
                # Prefer client_msg_id, fallback to event_ts + user + channel
                event_id = client_msg_id if client_msg_id else f"{event_ts}_{user_id}_{channel_id}"
                
                logger.info(f"📩 APP_MENTION detectado:")
                logger.info(f"   👤 Usuario: {user_id}")
                logger.info(f"   📺 Canal: {channel_id}")
                logger.info(f"   💬 Texto: {text}")
                logger.info(f"   🔑 Event ID: {event_id}")
                
                # Check for duplicate event
                if _is_event_processed(event_id):
                    logger.info(f"⏭️  Evento duplicado ignorado: {event_id}")
                    logger.info("=" * 60)
                    return {"ok": True}
                
                # Launch background task for processing
                asyncio.create_task(_process_app_mention_background(event, event_id))
                
                logger.info(f"🚀 Tarea en background iniciada para evento: {event_id}")
                logger.info("=" * 60)
                
                # Return 200 immediately to Slack
                # (Slack requires response within 3 seconds)
                return {"ok": True}
            
            # Handle message events in threads (conversation continuation)
            if event_type == "message":
                # Check if it's a thread message (not bot message, not system message)
                thread_ts = event.get('thread_ts')
                bot_id = event.get('bot_id')
                subtype = event.get('subtype')
                user_id = event.get('user')
                channel_id = event.get('channel')
                text = event.get('text', '')
                event_ts = event.get('event_ts', '')
                client_msg_id = event.get('client_msg_id', '')
                
                # Only process if:
                # 1. It's in a thread (thread_ts exists)
                # 2. It's not from the bot (no bot_id)
                # 3. It's not a system message (no subtype)
                # 4. Has a user (user_id exists)
                if thread_ts and not bot_id and not subtype and user_id:
                    # Create unique event ID for deduplication
                    event_id = client_msg_id if client_msg_id else f"{event_ts}_{user_id}_{channel_id}"
                    
                    logger.info(f"💬 MENSAJE EN THREAD detectado:")
                    logger.info(f"   👤 Usuario: {user_id}")
                    logger.info(f"   📺 Canal: {channel_id}")
                    logger.info(f"   🧵 Thread: {thread_ts}")
                    logger.info(f"   💬 Texto: {text}")
                    logger.info(f"   🔑 Event ID: {event_id}")
                    
                    # Check for duplicate event
                    if _is_event_processed(event_id):
                        logger.info(f"⏭️  Evento duplicado ignorado: {event_id}")
                        logger.info("=" * 60)
                        return {"ok": True}
                    
                    # Launch background task for processing (same as app_mention)
                    asyncio.create_task(_process_app_mention_background(event, event_id))
                    
                    logger.info(f"🚀 Tarea en background iniciada para mensaje en thread: {event_id}")
                    logger.info("=" * 60)
                    
                    return {"ok": True}
            
            # Ignore other event types
            logger.info(f"⚠️  Tipo de evento ignorado: {event_type}")
            logger.info("=" * 60)
            return {"ok": True}
        
        # Unknown event type
        logger.warning(f"⚠️  Tipo de evento desconocido: {event_type_main}")
        logger.info("=" * 60)
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"❌ ERROR procesando evento de Slack: {str(e)}", exc_info=True)
        logger.info("=" * 60)
        # Return 200 to Slack even on error to prevent retries
        return {"ok": True, "error": str(e)}


async def handle_app_mention(
    event: Dict[str, Any],
    slack_client: SlackClient,
    db: Session
):
    """
    Handle app_mention events and thread messages from Slack.
    Processes both @bot mentions and conversation continuations in threads.
    
    Args:
        event: Slack event data
        slack_client: Slack client instance
        db: Database session
    """
    try:
        logger.info("🔄 Iniciando procesamiento de mensaje...")
        
        # Extract event data
        user_id = event.get("user")
        channel_id = event.get("channel")
        text = event.get("text", "")
        message_ts = event.get("ts")
        thread_ts = event.get("thread_ts")  # If in a thread
        
        logger.info(f"📝 Texto original: '{text}'")
        
        # Remove bot mention from text
        cleaned_text = slack_client.remove_bot_mention(text)
        
        logger.info(f"🧹 Texto limpio (sin mención del bot): '{cleaned_text}'")
        
        if not cleaned_text:
            logger.warning("⚠️  Texto vacío después de limpiar. Ignorando mensaje.")
            return
        
        # Get user info
        logger.info(f"👤 Obteniendo información del usuario {user_id}...")
        try:
            user_info = slack_client.get_user_info(user_id)
            user_name = user_info.get("real_name") or user_info.get("name")
            user_email = user_info.get("profile", {}).get("email")
            logger.info(f"✅ Usuario: {user_name} ({user_email or 'sin email'})")
        except Exception as e:
            logger.warning(f"⚠️  No se pudo obtener info del usuario: {str(e)}")
            user_name = user_id
            user_email = None
        
        # Get channel info
        logger.info(f"📺 Obteniendo información del canal {channel_id}...")
        try:
            channel_info = slack_client.get_channel_info(channel_id)
            channel_name = channel_info.get("name", channel_id)
            logger.info(f"✅ Canal: #{channel_name}")
        except Exception as e:
            logger.warning(f"⚠️  No se pudo obtener info del canal: {str(e)}")
            channel_name = channel_id
        
        # Prepare bot process request
        logger.info("📦 Preparando request para el bot...")
        bot_request = BotProcessRequest(
            platform="slack",
            platform_message_id=message_ts,
            platform_channel_id=channel_id,
            platform_user_id=user_id,
            message_text=cleaned_text,
            user_name=user_name,
            channel_name=channel_name,
            user_email=user_email,
            metadata={
                "thread_ts": thread_ts,
                "event_ts": event.get("event_ts"),
                "channel_type": event.get("channel_type")
            }
        )
        
        logger.info(f"🤖 Enviando mensaje al endpoint del bot para procesamiento...")
        logger.info(f"   Plataforma: {bot_request.platform}")
        logger.info(f"   Usuario: {bot_request.user_name}")
        logger.info(f"   Canal: #{bot_request.channel_name}")
        logger.info(f"   Mensaje: '{bot_request.message_text}'")
        
        # Process message through bot endpoint
        bot_response = await process_message(bot_request, db)
        
        logger.info(f"✅ Respuesta recibida del bot (success={bot_response.success})")
        
        # Send response back to Slack
        if bot_response.success:
            logger.info(f"📤 Enviando respuesta a Slack:")
            logger.info(f"   Canal: {channel_id}")
            logger.info(f"   Thread: {thread_ts or message_ts}")
            logger.info(f"   Respuesta: '{bot_response.bot_response[:100]}...'")
            
            slack_client.send_message(
                channel=channel_id,
                text=bot_response.bot_response,
                thread_ts=thread_ts or message_ts  # Reply in thread if exists
            )
            
            logger.info("✅ Mensaje enviado exitosamente a Slack")
        else:
            logger.error(f"❌ Error en procesamiento del bot: {bot_response.error}")
            # Send error message to user
            slack_client.send_message(
                channel=channel_id,
                text="Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.",
                thread_ts=thread_ts or message_ts
            )
            logger.info("📤 Mensaje de error enviado al usuario")
            
    except Exception as e:
        logger.error(f"❌ Error procesando app_mention: {str(e)}", exc_info=True)
        # Try to send error message to user
        try:
            slack_client.send_message(
                channel=event.get("channel"),
                text="Lo siento, hubo un error inesperado. Por favor intenta de nuevo más tarde.",
                thread_ts=event.get("thread_ts") or event.get("ts")
            )
            logger.info("📤 Mensaje de error inesperado enviado al usuario")
        except Exception as e2:
            logger.error(f"❌ No se pudo enviar mensaje de error a Slack: {str(e2)}")


@router.post("/send")
async def send_slack_message(
    message_request: SlackMessageRequest
):
    """
    Send a message to Slack (for manual/admin use).
    
    Args:
        message_request: Message details
        
    Returns:
        Slack API response
    """
    try:
        slack_client = SlackClient()
        
        response = slack_client.send_message(
            channel=message_request.channel,
            text=message_request.text,
            thread_ts=message_request.thread_ts
        )
        
        return {
            "success": True,
            "message_ts": response["ts"],
            "channel": response["channel"]
        }
        
    except Exception as e:
        logger.error(f"Error sending message to Slack: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/health")
async def slack_health():
    """
    Health check for Slack connector.
    
    Returns:
        Status of Slack integration
    """
    try:
        slack_client = SlackClient()
        # Test authentication
        auth_response = slack_client.client.auth_test()
        
        logger.info(f"✅ Canal Slack conectado: bot_id={auth_response.get('user_id')}, team={auth_response.get('team')}")
        
        return {
            "status": "healthy",
            "connected": True,
            "bot_user_id": auth_response.get("user_id"),
            "team": auth_response.get("team")
        }
    except Exception as e:
        logger.error(f"❌ Canal Slack no conectado: {str(e)}")
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e)
        }

