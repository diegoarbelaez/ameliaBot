# 🔐 Variables de Entorno Mínimas para Render

Para que tu backend funcione en Render, configura estas variables en:
**Dashboard > botdo-backend > Environment**

## ✅ Variables REQUERIDAS (Mínimo para arrancar)

```bash
# 1. Base de Datos (ya configurada automáticamente)
DATABASE_URL=<ya-esta-configurada>

# 2. Seguridad
SECRET_KEY=<genera con: openssl rand -hex 32>

# 3. Slack
SLACK_BOT_TOKEN=xoxb-tu-token-aqui
SLACK_SIGNING_SECRET=tu-signing-secret-aqui

# 4. Whapi (WhatsApp)
WHAPI_API_KEY=tu-whapi-key-aqui
WHAPI_BASE_URL=https://gate.whapi.cloud
```

## 📝 Cómo Configurar

### 1. DATABASE_URL
✅ **Ya está configurada** si conectaste tu base de datos existente

### 2. SECRET_KEY
Genera una clave segura:
```bash
openssl rand -hex 32
```
Copia el resultado y pégalo como valor de `SECRET_KEY`

### 3. SLACK_BOT_TOKEN
1. Ve a [api.slack.com/apps](https://api.slack.com/apps)
2. Selecciona tu app
3. **OAuth & Permissions** > **Bot User OAuth Token**
4. Copia el token (empieza con `xoxb-`)

### 4. SLACK_SIGNING_SECRET
1. En la misma app de Slack
2. **Basic Information** > **App Credentials**
3. Copia el **Signing Secret**

### 5. WHAPI_API_KEY y WHAPI_BASE_URL
1. Ve a [whapi.cloud](https://whapi.cloud)
2. Dashboard > API Key
3. Copia tu API Key
4. Base URL: `https://gate.whapi.cloud`

---

## 🔧 Variables OPCIONALES (puedes agregarlas después)

```bash
# DigitalOcean (solo si usas esta integración)
DIGITALOCEAN_API_KEY=dop_v1_tu-token
DIGITALOCEAN_AGENT_ID=tu-agent-id

# Slack App Token (solo si usas Socket Mode)
SLACK_APP_TOKEN=xapp-tu-token

# CORS (por defecto permite todos los orígenes)
CORS_ORIGINS=https://botdo-frontend.onrender.com

# Ambiente y logs
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## 🚀 Después de Configurar

1. **Guardar** las variables en Render
2. El servicio se **re-deployará automáticamente**
3. Espera ~5 minutos
4. Verifica: `https://botdo-backend.onrender.com/health`

---

## ❓ ¿No tienes algún token?

### Sin Slack tokens
Si aún no tienes Slack configurado, puedes usar valores temporales:
```bash
SLACK_BOT_TOKEN=xoxb-temporary-token
SLACK_SIGNING_SECRET=temporary-secret
```
⚠️ **Nota**: Las funcionalidades de Slack no funcionarán hasta que pongas los tokens reales.

### Sin Whapi
Si no usarás WhatsApp de inmediato:
```bash
WHAPI_API_KEY=temporary-key
WHAPI_BASE_URL=https://gate.whapi.cloud
```
⚠️ **Nota**: Las funcionalidades de WhatsApp no funcionarán hasta que pongas los tokens reales.

### Sin DigitalOcean
No hay problema, es **opcional**. El backend arrancará sin estos valores.

---

## 📊 Checklist

Antes de que el backend funcione, asegúrate de tener:

- [ ] `DATABASE_URL` configurada (automática)
- [ ] `SECRET_KEY` generada y configurada
- [ ] `SLACK_BOT_TOKEN` configurado
- [ ] `SLACK_SIGNING_SECRET` configurado
- [ ] `WHAPI_API_KEY` configurado
- [ ] `WHAPI_BASE_URL` configurado

Una vez todas estén marcadas, el backend debería arrancar correctamente.

---

## 🆘 ¿Sigue fallando?

Revisa los logs:
```
Dashboard > botdo-backend > Logs
```

Busca el mensaje:
- ✅ `"All required environment variables loaded successfully"` = Éxito
- ❌ `"Required environment variable 'X' is not set"` = Falta variable X

