# 🔧 Cómo Obtener tu Token Real de Slack

## ❌ Problema Detectado

Tu archivo `.env` tiene el token de ejemplo:
```
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
```

Necesitas reemplazarlo con tu **token real** de Slack.

---

## ✅ Solución - Paso a Paso

### 1. Ve a tu App de Slack
🔗 [https://api.slack.com/apps](https://api.slack.com/apps)

### 2. Selecciona tu App
- Si no tienes una app, haz clic en **"Create New App"**
- Elige **"From scratch"**
- Dale un nombre (ej: "BotDO")
- Selecciona tu workspace

### 3. Configura los Permisos del Bot

Ve a **"OAuth & Permissions"** (en el menú lateral) y agrega estos **Bot Token Scopes**:

#### Permisos Requeridos:
- ✅ `app_mentions:read` - Leer menciones del bot
- ✅ `chat:write` - Enviar mensajes
- ✅ `channels:read` - Ver información de canales públicos
- ✅ `users:read` - Ver información de usuarios
- ✅ `users:read.email` - Ver emails de usuarios (opcional)

### 4. Instala el Bot en tu Workspace

En la misma página de **"OAuth & Permissions"**:
- Haz clic en **"Install to Workspace"** (o "Reinstall to Workspace")
- Autoriza los permisos
- ¡Ahora verás tu **Bot User OAuth Token**!

### 5. Copia el Token

Verás algo como:
```
Bot User OAuth Token
xoxb-XXXXXXXXXXXX-XXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXX
```

- Haz clic en **"Copy"** o copia el token completo
- Este es tu **token real** (debe empezar con `xoxb-` y tener 50+ caracteres)

### 6. Actualiza tu Archivo .env

Abre el archivo `.env` en la raíz del proyecto:

```bash
nano .env
# o usa tu editor favorito
```

Reemplaza esta línea:
```env
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
```

Con tu token real:
```env
SLACK_BOT_TOKEN=xoxb-XXXXXXXXXXXX-XXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXX
```

**⚠️ IMPORTANTE:** No compartas este token con nadie ni lo subas a GitHub.

### 7. También necesitas el Signing Secret

Mientras estás en la app de Slack:
1. Ve a **"Basic Information"**
2. Busca **"App Credentials"**
3. Copia el **"Signing Secret"**
4. Actualiza también esta línea en tu `.env`:

```env
SLACK_SIGNING_SECRET=tu_signing_secret_real
```

### 8. (Opcional) App-Level Token

Si planeas usar Socket Mode (no es necesario para webhooks):
1. En **"Basic Information"** → **"App-Level Tokens"**
2. Genera un token con el scope `connections:write`
3. Actualiza:

```env
SLACK_APP_TOKEN=xapp-tu-app-token-real
```

### 9. Reinicia los Contenedores

```bash
docker-compose down
docker-compose up -d
```

### 10. Verifica que Funcione

```bash
docker-compose exec backend python test_slack_auth.py
```

Deberías ver:
```
✅ ¡AUTENTICACIÓN EXITOSA!
```

---

## 🎯 Invitar el Bot a un Canal

Una vez configurado el token:

1. Ve a un canal de Slack donde quieras usar el bot
2. Escribe: `/invite @BotDO` (o el nombre de tu bot)
3. El bot ahora puede leer mensajes en ese canal

---

## 📝 Configurar Event Subscriptions

Para que el bot reciba eventos (menciones):

1. Ve a **"Event Subscriptions"** en tu app de Slack
2. Activa **"Enable Events"**
3. En **"Request URL"** pon:
   ```
   https://tu-dominio.com/canales/slack/events
   ```
   (Para desarrollo local, usa ngrok o similar)

4. En **"Subscribe to bot events"**, agrega:
   - `app_mention` - Cuando alguien menciona al bot

5. Guarda los cambios

---

## 🔍 Verificar Estado

Después de actualizar el token, puedes verificar el estado:

```bash
# Ver logs del backend
docker-compose logs -f backend

# Llamar al endpoint de health
curl http://localhost:8000/canales/slack/health
```

---

## ❓ Preguntas Frecuentes

### P: ¿Dónde encuentro mi workspace de Slack?
**R:** En la URL de Slack: `https://TU-WORKSPACE.slack.com`

### P: ¿El token caduca?
**R:** No, los tokens de bot no caducan automáticamente. Pero pueden ser revocados si desinstalas el bot.

### P: ¿Puedo usar el mismo bot en varios workspaces?
**R:** Necesitas instalar el bot en cada workspace y usar el token correspondiente de cada uno.

### P: ¿Qué pasa si veo "token_revoked"?
**R:** Reinstala el bot en el workspace y genera un nuevo token.

---

## 🆘 ¿Aún tienes problemas?

1. ✅ Verifica que el token empiece con `xoxb-`
2. ✅ Verifica que no haya espacios extra en el .env
3. ✅ Verifica que el bot esté instalado en tu workspace
4. ✅ Reinicia los contenedores después de cambiar el .env
5. ✅ Ejecuta el script de diagnóstico para más detalles

---

**¡Listo! Una vez tengas tu token real, el bot funcionará correctamente.** 🚀

