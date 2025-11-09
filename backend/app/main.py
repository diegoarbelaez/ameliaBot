from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Import routers
from app.routers import auth, messages, users, bot
from app.routers.connectors import slack, whapi


# ===================================
# Environment Variables Validation
# ===================================
def get_required_env(var_name: str) -> str:
    """
    Get required environment variable or raise error if not found.
    No default values - ensures security by forcing explicit configuration.
    """
    value = os.getenv(var_name)
    if value is None or value == "":
        raise EnvironmentError(
            f"Required environment variable '{var_name}' is not set. "
            f"Please check your .env file."
        )
    return value


def get_optional_env(var_name: str, default: str = None) -> str:
    """
    Get optional environment variable with optional default.
    """
    return os.getenv(var_name, default)


# Validate and load all required environment variables at startup
try:
    # Database (DATABASE_URL is primary, others are for Docker Compose only)
    DATABASE_URL = get_required_env("DATABASE_URL")
    POSTGRES_HOST = get_optional_env("POSTGRES_HOST", "db")
    POSTGRES_PORT = get_optional_env("POSTGRES_PORT", "5432")
    POSTGRES_DB = get_optional_env("POSTGRES_DB", "botdo")
    POSTGRES_USER = get_optional_env("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = get_optional_env("POSTGRES_PASSWORD", "")
    
    # Slack (required for Slack functionality)
    SLACK_BOT_TOKEN = get_required_env("SLACK_BOT_TOKEN")
    SLACK_APP_TOKEN = get_optional_env("SLACK_APP_TOKEN", "")  # Not always needed
    SLACK_SIGNING_SECRET = get_required_env("SLACK_SIGNING_SECRET")
    
    # Digital Ocean (optional - only needed for DO integration)
    DIGITALOCEAN_API_KEY = get_optional_env("DIGITALOCEAN_API_KEY", "")
    DIGITALOCEAN_AGENT_ID = get_optional_env("DIGITALOCEAN_AGENT_ID", "")
    DIGITALOCEAN_API_URL = get_optional_env("DIGITALOCEAN_API_URL", "https://api.digitalocean.com/v2")
    
    # Whapi (required for WhatsApp functionality)
    WHAPI_API_KEY = get_required_env("WHAPI_API_KEY")
    WHAPI_BASE_URL = get_required_env("WHAPI_BASE_URL")
    WHAPI_CHANNEL_ID = get_optional_env("WHAPI_CHANNEL_ID", "")
    
    # Security
    SECRET_KEY = get_required_env("SECRET_KEY")
    
    # CORS (allow all origins if not specified)
    CORS_ORIGINS_STR = get_optional_env("CORS_ORIGINS", "*")
    if CORS_ORIGINS_STR == "*":
        CORS_ORIGINS = ["*"]
    else:
        CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_STR.split(",")]
    
    # Optional
    ENVIRONMENT = get_optional_env("ENVIRONMENT", "production")
    LOG_LEVEL = get_optional_env("LOG_LEVEL", "INFO")
    
    print("✅ All required environment variables loaded successfully")
    
except EnvironmentError as e:
    print(f"❌ Environment Configuration Error: {e}", file=sys.stderr)
    print("💡 Please create a .env file based on .env.example", file=sys.stderr)
    sys.exit(1)


# Initialize FastAPI app
app = FastAPI(
    title="BotDO API",
    description="Backend API for Slack and Whapi bot integration with Digital Ocean Agent",
    version="1.0.0"
)

# Configure CORS with environment variables
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(users.router)
app.include_router(bot.router)
app.include_router(slack.router)
app.include_router(whapi.router)


@app.get("/")
async def root():
    """
    Hello World endpoint - root path
    """
    return {
        "message": "Hello World from BotDO Backend!",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    from app.database import engine
    
    # Check database connection
    db_status = "disconnected"
    try:
        with engine.connect() as conn:
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "service": "BotDO Backend",
        "environment": ENVIRONMENT,
        "database": db_status,
        "integrations": {
            "slack": "configured" if SLACK_BOT_TOKEN else "not_configured",
            "whapi": "configured" if WHAPI_API_KEY else "not_configured",
            "digitalocean": "configured" if DIGITALOCEAN_API_KEY else "not_configured"
        }
    }


@app.get("/api/test")
async def test_endpoint():
    """
    Test endpoint for frontend connectivity
    """
    return {
        "message": "Backend API is working correctly!",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "docs": "/docs",
            "test": "/api/test",
            "bot": "/bot/process",
            "slack_events": "/canales/slack/events",
            "slack_send": "/canales/slack/send",
            "whapi_events": "/canales/whapi/events",
            "whapi_send": "/canales/whapi/send"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

