# Quick Commands Reference - BotDO

Comandos rápidos y útiles para desarrollo y pruebas.

## 🗑️ Limpiar Base de Datos

```bash
# Con confirmación
./clean_database.sh

# Sin confirmación (para scripts)
./clean_database.sh --force
```

## 🐳 Docker Commands

```bash
# Iniciar todo
docker-compose up -d

# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f
docker-compose logs -f backend

# Reiniciar un servicio
docker-compose restart backend

# Reconstruir y reiniciar
docker-compose up --build -d

# Detener todo
docker-compose down

# Detener y eliminar volúmenes (⚠️ elimina la BD)
docker-compose down -v
```

## 🗄️ Database Commands

```bash
# Conectar a la base de datos
docker exec -it botdo_db psql -U postgres -d botdo

# Ver tablas
docker exec -it botdo_db psql -U postgres -d botdo -c "\dt"

# Contar registros
docker exec -it botdo_db psql -U postgres -d botdo -c "
SELECT 'Messages' as table, COUNT(*) FROM messages
UNION ALL SELECT 'Users', COUNT(*) FROM users
UNION ALL SELECT 'Channels', COUNT(*) FROM channels;
"

# Ver últimos mensajes
docker exec -it botdo_db psql -U postgres -d botdo -c "
SELECT message_id, channel, LEFT(message_text, 40), timestamp 
FROM messages 
ORDER BY timestamp DESC 
LIMIT 5;
"
```

## 🔧 Development Workflow

```bash
# 1. Start clean
docker-compose up -d
./clean_database.sh --force

# 2. Make changes to code
# ... edit files ...

# 3. Restart backend to apply changes
docker-compose restart backend

# 4. Test
# ... run tests ...

# 5. Check logs if needed
docker-compose logs -f backend

# 6. Clean for next test
./clean_database.sh --force
```

## 🧪 Testing Shortcuts

```bash
# Full reset (nuclear option)
docker-compose down -v
docker-compose up --build -d
./clean_database.sh --force

# Quick backend restart
docker-compose restart backend && docker-compose logs -f backend

# Check API health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

## 📊 Monitoring

```bash
# Real-time logs (all services)
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Database only
docker-compose logs -f db

# Last 50 lines
docker-compose logs --tail=50

# Container resource usage
docker stats botdo_backend botdo_db botdo_frontend
```

## 🔍 Debugging

```bash
# Enter backend container
docker exec -it botdo_backend /bin/bash

# Enter database container
docker exec -it botdo_db /bin/bash

# Check backend environment variables
docker exec botdo_backend env | grep -E '(POSTGRES|SLACK|WHAPI|DO_)'

# Test database connection from backend
docker exec botdo_backend python -c "from app.database import engine; print('DB Connected!' if engine else 'Failed')"
```

## 📝 Log Files

```bash
# Save logs to file
docker-compose logs > logs_$(date +%Y%m%d_%H%M%S).txt

# Save only backend logs
docker-compose logs backend > backend_logs_$(date +%Y%m%d_%H%M%S).txt

# Watch and save
docker-compose logs -f | tee live_logs_$(date +%Y%m%d_%H%M%S).txt
```

## 🔄 Environment Updates

```bash
# After changing .env file
docker-compose down
docker-compose up -d

# Validate .env
python backend/validate_env.py
```

## 📚 Documentation Quick Links

- Full cleanup guide: `documentation/DATABASE_CLEANUP.md`
- Testing workflow: `documentation/TESTING_WORKFLOW.md`
- Environment setup: `documentation/ENV_SETUP.md`
- Deployment guide: `documentation/DEPLOYMENT.md`

