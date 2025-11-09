# BotDO - Slack & Whapi Integration Bot

A Docker-based bot application that connects Slack and Whapi with Digital Ocean Agent.

## Project Structure

```
botDO/
├── docker-compose.yml
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── database/         # PostgreSQL initialization
└── documentation/    # Project documentation
```

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Environment Variables

**⚠️ IMPORTANT: You must configure environment variables before running the application!**

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials:**
   ```bash
   nano .env
   ```

3. **Validate your configuration:**
   ```bash
   python backend/validate_env.py
   ```

**📖 For detailed instructions on getting credentials, see [ENV_SETUP.md](documentation/ENV_SETUP.md)**

The application requires the following categories of environment variables:
- ✅ **Database**: PostgreSQL connection settings
- ✅ **Slack**: Bot tokens and signing secrets
- ✅ **Digital Ocean**: API keys and agent configuration
- ✅ **Whapi**: WhatsApp API credentials
- ✅ **Security**: Secret keys for encryption
- ✅ **CORS**: Allowed origins for API access

**Note:** The application will refuse to start if required variables are missing. This is a security feature!

### Running the Application

```bash
# 1. First time setup - validate environment variables
python backend/validate_env.py

# 2. Build and start all services
docker-compose up --build

# 3. Stop all services
docker-compose down

# 4. View logs
docker-compose logs -f

# 5. Restart a specific service
docker-compose restart backend
```

### Access Points

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Database**: localhost:5432

## 🚀 Production Deployment

### Deploy to Render.com (Recommended)

**Quick Start:**
```bash
# 1. Verify everything is ready
./pre-deploy-check.sh

# 2. Push to GitHub
git push origin main

# 3. Follow the quick guide
# See RENDER_QUICK_START.md for 5-minute setup
```

**Resources:**
- 📖 **Quick Start**: [RENDER_QUICK_START.md](RENDER_QUICK_START.md) - Deploy in ~30 minutes
- 📚 **Complete Guide**: [documentation/RENDER_DEPLOYMENT.md](documentation/RENDER_DEPLOYMENT.md) - Detailed step-by-step
- 💰 **Cost**: Free tier available, $7/month for database after 90 days

**Why Render?**
- ✅ Free tier to start
- ✅ Auto-deploy from GitHub
- ✅ Managed PostgreSQL
- ✅ Zero-downtime deployments
- ✅ Free SSL/HTTPS

## Features

- ✅ Multi-platform message routing (Slack, WhatsApp, Web)
- ✅ Unified message database
- ✅ RESTful API with FastAPI
- ✅ Real-time message processing
- ✅ Digital Ocean Agent integration
- ✅ Admin authentication and user management
- ✅ Docker containerization
- ✅ Production-ready deployment

## 🛠️ Development Tools

### Database Cleanup Script

Quick script to reset the database to a fresh state for testing:

```bash
# Interactive mode (asks for confirmation)
./clean_database.sh

# Force mode (no confirmation)
./clean_database.sh --force
```

This script removes all test data from `messages`, `channels`, and `users` tables while keeping `admin_users` intact.

📖 **See [DATABASE_CLEANUP.md](documentation/DATABASE_CLEANUP.md) for full documentation**

## 📚 Documentation

### Deployment & Production
- 🚀 **[RENDER_QUICK_START.md](RENDER_QUICK_START.md)** - Deploy to Render in 30 minutes
- 📖 **[RENDER_DEPLOYMENT.md](documentation/RENDER_DEPLOYMENT.md)** - Complete Render deployment guide
- 🔧 **[DEPLOYMENT.md](documentation/DEPLOYMENT.md)** - General deployment guide

### Development
- 🔐 **[ENV_SETUP.md](documentation/ENV_SETUP.md)** - Environment variables setup
- 🗄️ **[DATABASE_CLEANUP.md](documentation/DATABASE_CLEANUP.md)** - Database cleanup helper
- 📋 **[BOT_ARCHITECTURE.md](documentation/BOT_ARCHITECTURE.md)** - System architecture
- 📝 **[CHANGES_SUMMARY.md](documentation/CHANGES_SUMMARY.md)** - Recent changes

### Guides & Tutorials
- 🧪 **[TESTING_WORKFLOW.md](documentation/TESTING_WORKFLOW.md)** - Testing guidelines
- 📊 **[LOGGING_GUIDE.md](documentation/LOGGING_GUIDE.md)** - Logging best practices
- ⚡ **[QUICK_START.md](documentation/QUICK_START.md)** - Quick start guide

**Full documentation index:** [documentation/README.md](documentation/README.md)

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11, SQLAlchemy
- **Frontend**: React 18, Nginx
- **Database**: PostgreSQL 15
- **Deployment**: Docker, Render.com
- **Integrations**: Slack API, Whapi, DigitalOcean

