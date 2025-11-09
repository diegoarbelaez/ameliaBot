# Guía Rápida - BotDO

## Inicio Rápido

### 1. Instalación

```bash
# Clonar repositorio (si aplica)
cd /path/to/botDO

# Instalar dependencias del backend
cd backend
pip install -r requirements.txt

# Instalar dependencias del frontend (si aplica)
cd ../frontend
npm install
```

### 2. Configuración

Crear archivo `.env` en `backend/`:

```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/botdo
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=botdo
POSTGRES_USER=user
POSTGRES_PASSWORD=password

# Slack
SLACK_BOT_TOKEN=xoxb-tu-token-aqui
SLACK_APP_TOKEN=xapp-tu-token-aqui
SLACK_SIGNING_SECRET=tu-secret-aqui

# Digital Ocean
DIGITALOCEAN_API_KEY=tu-api-key-aqui
DIGITALOCEAN_AGENT_ID=tu-agent-id-aqui
DIGITALOCEAN_API_URL=https://api.digitalocean.com/v2

# WhatsApp/Whapi (opcional por ahora)
WHAPI_API_KEY=tu-api-key
WHAPI_BASE_URL=https://api.whapi.cloud

# Seguridad
SECRET_KEY=tu-secret-key-super-seguro-aqui

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 3. Iniciar con Docker (Recomendado)

```bash
# Desde el directorio raíz
docker-compose up -d

# Ver logs
docker-compose logs -f backend
```

### 4. Iniciar sin Docker

```bash
# Terminal 1 - Base de datos (si no usas Docker)
# Asegúrate de tener PostgreSQL instalado y corriendo

# Terminal 2 - Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3 - Frontend (opcional)
cd frontend
npm start
```

### 5. Verificar Instalación

```bash
# Health check general
curl http://localhost:8000/health

# Health check del bot
curl http://localhost:8000/bot/health

# Health check de Slack
curl http://localhost:8000/canales/slack/health

# Ver documentación interactiva
open http://localhost:8000/docs
```

## Configurar Slack

### 1. Crear App en Slack

1. Ir a https://api.slack.com/apps
2. Click en "Create New App" → "From scratch"
3. Nombrar la app (ej: "BotDO")
4. Seleccionar workspace

### 2. Configurar Permisos

En "OAuth & Permissions" → "Bot Token Scopes", agregar:
- `app_mentions:read`
- `chat:write`
- `channels:read`
- `users:read`
- `users:read.email`

### 3. Instalar App

1. En "Install App", click en "Install to Workspace"
2. Autorizar la app
3. Copiar "Bot User OAuth Token" → Variable `SLACK_BOT_TOKEN`
4. En "Basic Information", copiar "Signing Secret" → Variable `SLACK_SIGNING_SECRET`

### 4. Configurar Eventos (Requiere URL pública)

**Opción A: Desarrollo Local con ngrok**

```bash
# Instalar ngrok
brew install ngrok  # macOS
# o descargar de https://ngrok.com/

# Exponer puerto local
ngrok http 8000

# Copiar URL HTTPS (ej: https://abc123.ngrok.io)
```

**Opción B: Servidor en Producción**

Usar tu dominio/IP pública directamente.

**Configurar en Slack:**

1. En "Event Subscriptions", activar eventos
2. Request URL: `https://tu-url-aqui/canales/slack/events`
3. En "Subscribe to bot events", agregar:
   - `app_mention`
4. Guardar cambios

### 5. Probar

En Slack, menciona al bot:
```
@BotDO hola, ¿cómo estás?
```

El bot debería responder automáticamente.

## Arquitectura en 30 Segundos

```
Usuario en Slack → Menciona @BotDO
         ↓
Slack envía evento → /canales/slack/events
         ↓
Se verifica firma de seguridad
         ↓
Se extrae mensaje → /bot/process
         ↓
Se guarda en BD + Se obtiene historial
         ↓
Se envía a Digital Ocean Agent
         ↓
Se recibe respuesta del Agent
         ↓
Se guarda respuesta en BD
         ↓
Se envía respuesta a Slack
         ↓
Usuario ve respuesta del bot
```

## Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Hello World |
| `/health` | GET | Estado general del sistema |
| `/docs` | GET | Documentación interactiva (Swagger) |
| `/bot/process` | POST | Procesar mensaje (interno) |
| `/bot/health` | GET | Estado del servicio del bot |
| `/canales/slack/events` | POST | Webhook de Slack |
| `/canales/slack/send` | POST | Enviar mensaje a Slack |
| `/canales/slack/health` | GET | Estado de conexión Slack |
| `/api/messages` | GET | Listar mensajes (requiere auth) |

## Probar Endpoints Manualmente

### 1. Probar Bot Directamente

```bash
curl -X POST http://localhost:8000/bot/process \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "slack",
    "platform_message_id": "test-123",
    "platform_channel_id": "C01234567",
    "platform_user_id": "U01234567",
    "message_text": "Hola bot",
    "user_name": "Test User",
    "channel_name": "#general"
  }'
```

### 2. Enviar Mensaje a Slack

```bash
curl -X POST http://localhost:8000/canales/slack/send \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "C01234567",
    "text": "Hola desde la API"
  }'
```

### 3. Ver Mensajes (requiere autenticación)

```bash
# Primero obtener token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "tu-password"
  }'

# Usar el token para listar mensajes
curl http://localhost:8000/api/messages \
  -H "Authorization: Bearer TU-TOKEN-AQUI"
```

## Troubleshooting

### Error: "Invalid signature" en Slack

**Solución:**
- Verificar que `SLACK_SIGNING_SECRET` sea correcto
- Asegurarse de que el request llegue directamente desde Slack
- Si usas proxy, verificar que headers se preserven

### Bot no responde

**Solución:**
1. Verificar que el bot esté instalado: `/canales/slack/health`
2. Verificar eventos en Slack: App → "Event Subscriptions"
3. Revisar logs: `docker-compose logs -f backend`
4. Verificar que el bot tenga permisos correctos

### Error de conexión a Digital Ocean

**Solución:**
- Verificar `DIGITALOCEAN_API_KEY` en `.env`
- Verificar `DIGITALOCEAN_AGENT_ID` en `.env`
- Probar health check: `/bot/health`
- Verificar conectividad de red

### Error de base de datos

**Solución:**
- Verificar que PostgreSQL esté corriendo
- Verificar credenciales en `DATABASE_URL`
- Ejecutar migraciones si es necesario
- Verificar que las tablas existan

## Comandos Útiles

```bash
# Ver logs del backend
docker-compose logs -f backend

# Reiniciar servicios
docker-compose restart

# Detener todos los servicios
docker-compose down

# Reconstruir containers
docker-compose up -d --build

# Acceder a shell del backend
docker-compose exec backend bash

# Acceder a PostgreSQL
docker-compose exec db psql -U botdo

# Ver tablas en la BD
docker-compose exec db psql -U botdo -c "\dt"
```

## Estructura del Proyecto

```
botDO/
├── backend/
│   ├── app/
│   │   ├── services/          # Lógica de negocio
│   │   ├── routers/           # Endpoints de la API
│   │   │   └── connectors/    # Conectores de plataformas
│   │   ├── models.py          # Modelos de base de datos
│   │   ├── schemas.py         # Schemas Pydantic
│   │   └── main.py            # Punto de entrada
│   ├── requirements.txt       # Dependencias Python
│   └── Dockerfile
├── frontend/                  # Aplicación React
├── database/
│   └── init.sql              # Script inicial de BD
├── documentation/             # Documentación detallada
├── docker-compose.yml
└── QUICK_START.md            # Este archivo
```

## Documentación Adicional

- **Arquitectura Completa**: `documentation/BOT_ARCHITECTURE.md`
- **Resumen de Implementación**: `documentation/IMPLEMENTATION_SUMMARY.md`
- **Deployment**: `documentation/DEPLOYMENT.md`
- **Configuración de Entorno**: `documentation/ENV_SETUP.md`

## Soporte

Para más información:
1. Revisar documentación en `documentation/`
2. Ver logs del sistema
3. Consultar documentación de Swagger en `/docs`
4. Revisar código fuente (está bien comentado)

## Próximos Pasos

Una vez que todo funcione:

1. ✅ Probar integración con Slack en producción
2. ⏳ Configurar WhatsApp/Whapi
3. ⏳ Personalizar respuestas del bot
4. ⏳ Agregar comandos especiales
5. ⏳ Configurar monitoreo y alertas

---

¡Tu bot está listo para usar! 🚀

