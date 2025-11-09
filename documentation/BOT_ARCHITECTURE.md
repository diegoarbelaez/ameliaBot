# Arquitectura del Bot - BotDO

## Descripción General

La arquitectura del bot sigue un patrón de conectores que permite integrar múltiples plataformas de mensajería (Slack, WhatsApp, Web) con un procesamiento centralizado de mensajes y respuestas generadas por IA.

## Flujo de Datos

```
┌─────────────┐
│   Slack     │
│  WhatsApp   │──┐
│    Web      │  │
└─────────────┘  │
                 ▼
         ┌──────────────┐
         │  Conectores  │
         │  /canales/   │
         └──────┬───────┘
                │
                ▼
      ┌──────────────────┐
      │ Message Service  │
      │  - Save message  │
      │  - Get history   │
      │  - Format OpenAI │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │  Bot Endpoint    │
      │  /bot/process    │
      └────────┬─────────┘
               │
               ▼
    ┌────────────────────┐
    │ Digital Ocean      │
    │ AI Agent           │
    └────────┬───────────┘
             │
             ▼
       Bot Response
```

## Componentes

### 1. Message Service (`app/services/message_service.py`)

Servicio centralizado para gestión de mensajes, usuarios y canales.

**Funciones principales:**
- `get_or_create_user()` - Gestiona usuarios de diferentes plataformas
- `get_or_create_channel()` - Gestiona canales de diferentes plataformas
- `save_message()` - Guarda mensajes en la base de datos
- `get_conversation_history()` - Obtiene últimos 20 mensajes
- `format_to_openai()` - Convierte mensajes a formato OpenAI

**Formato OpenAI:**
```json
[
  {"role": "user", "content": "Hola, ¿cómo estás?"},
  {"role": "assistant", "content": "¡Hola! Estoy bien, gracias."},
  {"role": "user", "content": "¿Puedes ayudarme?"}
]
```

### 2. Digital Ocean Client (`app/services/digitalocean_client.py`)

Cliente para interactuar con el agente de IA de Digital Ocean.

**Funciones:**
- `send_to_agent()` - Envía conversación y recibe respuesta
- `health_check()` - Verifica disponibilidad del agente

**Variables de entorno requeridas:**
- `DIGITALOCEAN_API_KEY` - API key de Digital Ocean
- `DIGITALOCEAN_AGENT_ID` - ID del agente configurado
- `DIGITALOCEAN_API_URL` - URL base de la API (opcional)

### 3. Bot Endpoint (`app/routers/bot.py`)

Endpoint principal que orquesta el procesamiento de mensajes.

**POST `/bot/process`**

Request:
```json
{
  "platform": "slack",
  "platform_message_id": "1234.5678",
  "platform_channel_id": "C01234567",
  "platform_user_id": "U01234567",
  "message_text": "Hola bot",
  "user_name": "Diego",
  "channel_name": "#general",
  "user_email": "diego@example.com",
  "metadata": {}
}
```

Response:
```json
{
  "success": true,
  "bot_response": "¡Hola Diego! ¿En qué puedo ayudarte?",
  "message_id": "uuid-del-mensaje"
}
```

**Flujo de procesamiento:**
1. Crear/actualizar usuario y canal
2. Guardar mensaje entrante (inbound/user)
3. Obtener últimos 20 mensajes del canal
4. Formatear a OpenAI
5. Enviar a Digital Ocean Agent
6. Guardar respuesta del bot (outbound/bot)
7. Retornar respuesta

### 4. Slack Connector (`app/routers/connectors/slack.py`)

Conector para integración con Slack.

**POST `/canales/slack/events`**
- Recibe eventos de Slack Event API
- Verifica firma de seguridad
- Maneja eventos de tipo `app_mention`
- Procesa el mensaje y envía respuesta

**POST `/canales/slack/send`**
- Envía mensajes manualmente a Slack
- Para uso administrativo o testing

**GET `/canales/slack/health`**
- Verifica estado de la conexión con Slack

**Variables de entorno requeridas:**
- `SLACK_BOT_TOKEN` - Token del bot (xoxb-...)
- `SLACK_SIGNING_SECRET` - Secret para verificar requests
- `SLACK_APP_TOKEN` - Token de la app (xapp-...)

### 5. Slack Client (`app/services/slack_client.py`)

Cliente para interactuar con la API de Slack.

**Funciones:**
- `verify_slack_signature()` - Verifica autenticidad de requests
- `send_message()` - Envía mensajes a Slack
- `get_user_info()` - Obtiene información de usuario
- `get_channel_info()` - Obtiene información de canal
- `remove_bot_mention()` - Limpia menciones del texto

### 6. WhatsApp/Whapi Connector (Futuro)

Stub creado en `app/routers/connectors/whapi.py` para futura implementación.

## Base de Datos

### Tablas Principales

1. **users** - Usuarios de todas las plataformas
   - `platform` - slack, whatsapp, web
   - `platform_user_id` - ID del usuario en la plataforma
   - `display_name`, `email` - Información del usuario
   - `platform_metadata` - Datos adicionales en JSON

2. **channels** - Canales de todas las plataformas
   - `platform` - slack, whatsapp, web
   - `channel_id` - ID del canal en la plataforma
   - `channel_name` - Nombre del canal
   - `is_active` - Estado del canal
   - `platform_metadata` - Datos adicionales en JSON

3. **messages** - Mensajes unificados
   - `message_id` - ID único del mensaje (de la plataforma)
   - `channel` - Plataforma de origen
   - `direction` - inbound/outbound
   - `sender_type` - user/bot
   - `message_text` - Contenido del mensaje
   - `timestamp` - Timestamp original
   - `user_id` - Relación con usuario
   - `channel_id` - Relación con canal
   - `platform_metadata` - Datos adicionales en JSON

## Configuración de Slack

### 1. Crear Slack App

1. Ir a https://api.slack.com/apps
2. Crear nueva app "From scratch"
3. Dar nombre y seleccionar workspace

### 2. Configurar Permisos (OAuth & Permissions)

Bot Token Scopes necesarios:
- `app_mentions:read` - Leer menciones al bot
- `chat:write` - Enviar mensajes
- `channels:read` - Leer info de canales
- `users:read` - Leer info de usuarios
- `users:read.email` - Leer emails de usuarios

### 3. Habilitar Event Subscriptions

1. En "Event Subscriptions", habilitar eventos
2. Request URL: `https://tu-dominio.com/canales/slack/events`
3. Subscribe to bot events:
   - `app_mention` - Cuando mencionan al bot

### 4. Instalar App en Workspace

1. Ir a "Install App"
2. Instalar en workspace
3. Copiar "Bot User OAuth Token" → `SLACK_BOT_TOKEN`
4. Copiar "Signing Secret" → `SLACK_SIGNING_SECRET`

### 5. Probar Integración

```bash
# Verificar salud de la integración
curl http://localhost:8000/canales/slack/health

# En Slack, mencionar al bot
@BotDO hola, ¿cómo estás?
```

## Testing Local

### 1. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Crear archivo `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/botdo
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=botdo
POSTGRES_USER=user
POSTGRES_PASSWORD=password

# Slack
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
SLACK_SIGNING_SECRET=your-secret

# Digital Ocean
DIGITALOCEAN_API_KEY=your-api-key
DIGITALOCEAN_AGENT_ID=your-agent-id

# Security
SECRET_KEY=your-secret-key

# CORS
CORS_ORIGINS=http://localhost:3000
```

### 3. Usar ngrok para Webhooks

```bash
# Instalar ngrok
brew install ngrok  # macOS

# Exponer puerto local
ngrok http 8000

# Copiar URL HTTPS de ngrok y configurar en Slack:
# https://abc123.ngrok.io/canales/slack/events
```

### 4. Iniciar Servidor

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Probar Endpoints

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

## Monitoreo y Logs

Los logs se generan automáticamente para:
- Recepción de eventos de Slack
- Procesamiento de mensajes
- Llamadas a Digital Ocean Agent
- Errores y excepciones

Ver logs:
```bash
# Si se ejecuta con uvicorn
tail -f logs/app.log

# Si se ejecuta en Docker
docker-compose logs -f backend
```

## Próximos Pasos

1. ✅ Arquitectura base implementada
2. ✅ Conector de Slack funcional
3. ⏳ Testing con Slack en producción
4. ⏳ Implementar conector de WhatsApp/Whapi
5. ⏳ Agregar rate limiting
6. ⏳ Implementar sistema de reintentos
7. ⏳ Agregar métricas y analytics
8. ⏳ Implementar comandos especiales del bot

## Troubleshooting

### Error: "Invalid signature"
- Verificar que `SLACK_SIGNING_SECRET` sea correcto
- Verificar que la URL en Slack apunte al endpoint correcto

### Error: "DIGITALOCEAN_API_KEY not set"
- Asegurarse de que el `.env` esté en el directorio correcto
- Verificar que la variable esté correctamente definida

### Bot no responde en Slack
- Verificar que el bot esté instalado en el workspace
- Verificar que tenga los permisos necesarios
- Verificar que los eventos estén suscritos correctamente
- Revisar logs del servidor

### Mensajes duplicados
- El servicio de mensajes verifica automáticamente duplicados por `message_id`
- Si se reciben duplicados, verificar la lógica de Slack retry

## Soporte

Para dudas o problemas, revisar:
1. Logs del servidor
2. Documentación de Slack API: https://api.slack.com/
3. Digital Ocean AI Agents: https://docs.digitalocean.com/

