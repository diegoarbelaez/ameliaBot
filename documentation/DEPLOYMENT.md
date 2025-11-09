# BotDO - Deployment Guide

## ✅ Setup Complete!

Your Docker-based development environment is now fully operational with all services running successfully.

## Services Status

All containers are running and verified:

- ✅ **Backend (FastAPI)** - Running on http://localhost:8000
- ✅ **Frontend (React)** - Running on http://localhost:3000
- ✅ **Database (PostgreSQL)** - Running on localhost:5432

## Verification Results

### Backend API
- **Root Endpoint**: http://localhost:8000 ✓
- **Health Check**: http://localhost:8000/health ✓
- **API Docs**: http://localhost:8000/docs ✓

### Database
Successfully initialized with the following tables:
- `slack_messages` - Store Slack message data
- `whapi_messages` - Store Whapi message data
- `bot_config` - Bot configuration settings
- `message_routes` - Message routing rules
- `do_agent_logs` - Digital Ocean Agent interaction logs

### Frontend
- React development server compiled successfully
- Connected to backend API
- Accessible at http://localhost:3000

## Quick Start Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild Containers
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## Testing the APIs

### Backend Endpoints

```bash
# Hello World
curl http://localhost:8000

# Health Check
curl http://localhost:8000/health

# Test Endpoint
curl http://localhost:8000/api/test
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it botdo_db psql -U postgres -d botdo

# List all tables
docker exec botdo_db psql -U postgres -d botdo -c "\dt"

# Query bot config
docker exec botdo_db psql -U postgres -d botdo -c "SELECT * FROM bot_config;"
```

## Next Steps for Development

### 1. Slack Integration
- Add Slack Bot token to `.env`
- Implement webhook handlers in `backend/app/main.py`
- Create Slack message processing logic

### 2. Whapi Integration
- Add Whapi API credentials to `.env`
- Implement Whapi webhook handlers
- Create message routing between Slack and Whapi

### 3. Digital Ocean Agent
- Add DO Agent configuration to `.env`
- Implement agent interaction endpoints
- Create logging and monitoring

## File Structure

```
botDO/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       └── main.py          # FastAPI application
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.jsx          # React main component
│       ├── App.css          # Styles
│       ├── index.js
│       └── index.css
├── database/
│   └── init.sql             # Database initialization
├── docker-compose.yml       # Docker orchestration
├── .gitignore
├── README.md
└── DEPLOYMENT.md            # This file
```

## Troubleshooting

### Port Already in Use
If you see port conflict errors:
```bash
# Find and stop the process using the port
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:5432 | xargs kill -9  # Database
```

### Container Issues
```bash
# Remove all containers and volumes
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

## Environment Variables

Create a `.env` file in the root directory with your API keys:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=botdo

# Slack
SLACK_BOT_TOKEN=your_token_here
SLACK_SIGNING_SECRET=your_secret_here

# Whapi
WHAPI_API_KEY=your_key_here
WHAPI_BASE_URL=your_url_here

# Digital Ocean
DO_AGENT_API_KEY=your_key_here
```

## Support

For issues or questions:
1. Check container logs: `docker-compose logs [service]`
2. Verify all services are running: `docker-compose ps`
3. Restart services: `docker-compose restart`

---

**Happy Coding! 🚀**

