# 🚀 Render Deployment - Quick Start

## ⚡ Pasos Rápidos para Deployment

### 1️⃣ Preparar Repositorio (2 minutos)

```bash
# Asegúrate de que todos los cambios estén en GitHub
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2️⃣ Crear Cuenta en Render (2 minutos)

1. Ve a [render.com](https://render.com)
2. "Get Started" con GitHub
3. Autoriza acceso a tu repositorio

### 3️⃣ Deploy con Blueprint (1 clic, 15-20 minutos)

1. Dashboard > **"New +"** > **"Blueprint"**
2. Selecciona tu repositorio **botDO**
3. Render detecta automáticamente `render.yaml`
4. Clic en **"Apply"**

✨ **¡Listo!** Render creará automáticamente:
- ✅ PostgreSQL Database
- ✅ Backend FastAPI
- ✅ Frontend React

### 4️⃣ Configurar Variables de Entorno (5 minutos)

**Backend (botdo-backend):**

```bash
# Seguridad
SECRET_KEY=<openssl rand -hex 32>
ENVIRONMENT=production

# APIs
SLACK_BOT_TOKEN=xoxb-tu-token
SLACK_SIGNING_SECRET=tu-secret
WHAPI_API_KEY=tu-key
WHAPI_BASE_URL=https://gate.whapi.cloud
DO_API_TOKEN=dop_v1_tu-token
```

**Frontend (botdo-frontend):**

```bash
REACT_APP_API_URL=https://botdo-backend.onrender.com
```

### 5️⃣ Inicializar Base de Datos (3 minutos)

```bash
# Opción A: Desde tu terminal
psql <connection-string-de-render> < database/render-init.sql

# Opción B: Desde Render Dashboard
# Dashboard > botdo-db > Query > pega contenido de render-init.sql
```

### 6️⃣ Verificar Deployment (2 minutos)

✅ Backend: `https://botdo-backend.onrender.com/health`  
✅ Docs: `https://botdo-backend.onrender.com/docs`  
✅ Frontend: `https://botdo-frontend.onrender.com`

---

## 📊 Resumen

| Aspecto | Detalle |
|---------|---------|
| **Tiempo Total** | ~30 minutos |
| **Costo Inicial** | $0 (Free tier) |
| **Costo después de 90 días** | $7/mes (solo DB) |
| **Auto-deploy** | ✅ Habilitado |
| **SSL/HTTPS** | ✅ Incluido gratis |
| **Custom Domain** | ✅ Disponible |

---

## 📚 Documentación Completa

Para guía detallada paso a paso: **[documentation/RENDER_DEPLOYMENT.md](documentation/RENDER_DEPLOYMENT.md)**

---

## 🆘 Problemas Comunes

### Service no inicia
```bash
Dashboard > Service > Logs
# Verificar errores y variables de entorno
```

### Database connection error
```bash
# Verificar que DATABASE_URL esté conectado
Dashboard > botdo-backend > Environment
```

### Frontend no conecta con Backend
```bash
# Verificar URL del backend
Dashboard > botdo-frontend > Environment > REACT_APP_API_URL
# Debe ser: https://botdo-backend.onrender.com (con HTTPS)
```

---

## 🎯 Después del Deployment

### Configurar Webhooks

**Slack:**
- URL: `https://botdo-backend.onrender.com/api/connectors/slack/events`

**Whapi:**
- URL: `https://botdo-backend.onrender.com/api/connectors/whapi/webhook`

### Monitoreo

```bash
# Ver logs en tiempo real
Dashboard > Service > Logs > Live
```

### Futuras Actualizaciones

```bash
# ¡Solo haz push!
git push origin main
# Render auto-deploye automáticamente ✨
```

---

## 💡 Tips Pro

1. **Evitar Sleep (Free Tier)**: Usa [UptimeRobot](https://uptimerobot.com) para ping cada 5 minutos
2. **Custom Domain**: Dashboard > Service > Settings > Custom Domain
3. **Backups DB**: Automáticos en plan paid ($7/mes)
4. **Scaling**: Upgrade individual de servicios según necesites

---

## 🚀 ¡Ya está en producción!

**URLs:**
- 🌐 App: `https://botdo-frontend.onrender.com`
- 🔌 API: `https://botdo-backend.onrender.com`
- 📚 Docs: `https://botdo-backend.onrender.com/docs`

---

**¿Necesitas ayuda?** Revisa [RENDER_DEPLOYMENT.md](documentation/RENDER_DEPLOYMENT.md) para guía completa.

