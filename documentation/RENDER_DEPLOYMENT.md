# 🚀 Guía Completa de Deployment en Render.com

Esta guía te llevará paso a paso para deployar **AmeliaBot/BotDO** en Render.com desde cero.

---

## 📋 Tabla de Contenidos

1. [Pre-requisitos](#pre-requisitos)
2. [Preparación del Repositorio](#preparación-del-repositorio)
3. [Crear Cuenta en Render](#crear-cuenta-en-render)
4. [Deployment Paso a Paso](#deployment-paso-a-paso)
5. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
6. [Inicializar Base de Datos](#inicializar-base-de-datos)
7. [Verificación del Deployment](#verificación-del-deployment)
8. [Configuración de Webhooks](#configuración-de-webhooks)
9. [Troubleshooting](#troubleshooting)
10. [Costos y Planes](#costos-y-planes)

---

## 📌 Pre-requisitos

Antes de comenzar, asegúrate de tener:

- ✅ Cuenta de GitHub/GitLab/Bitbucket con tu repositorio
- ✅ Proyecto con Docker configurado (ya lo tienes ✓)
- ✅ Tokens de API necesarios:
  - Slack Bot Token
  - Slack Signing Secret
  - Whapi API Key
  - DigitalOcean API Token

---

## 📦 Preparación del Repositorio

### 1. Verificar Archivos de Producción

Asegúrate de que estos archivos existan en tu repositorio:

```bash
# Verificar archivos necesarios
ls render.yaml
ls backend/Dockerfile.prod
ls frontend/Dockerfile.prod
ls frontend/nginx.conf
ls database/render-init.sql
ls render.env.example
```

### 2. Subir Cambios a GitHub

```bash
# Agregar archivos nuevos
git add .

# Commit
git commit -m "Add Render.com deployment configuration"

# Push a tu repositorio
git push origin main
```

⚠️ **IMPORTANTE**: Asegúrate de que tu archivo `.env` NO esté en el repositorio (debe estar en `.gitignore`).

---

## 🌐 Crear Cuenta en Render

1. **Ve a** [render.com](https://render.com)
2. **Clic en** "Get Started for Free"
3. **Regístrate con GitHub** (recomendado para auto-deploy)
4. **Autoriza a Render** para acceder a tus repositorios

---

## 🚀 Deployment Paso a Paso

### Opción A: Deployment Automático con Blueprint (Recomendado)

#### Paso 1: Crear desde Blueprint

1. En el Dashboard de Render, clic en **"New +"**
2. Selecciona **"Blueprint"**
3. Conecta tu repositorio de GitHub
4. Render detectará automáticamente el archivo `render.yaml`
5. Clic en **"Apply"**

✨ Render creará automáticamente:
- Base de datos PostgreSQL (botdo-db)
- Backend FastAPI (botdo-backend)
- Frontend React (botdo-frontend)

#### Paso 2: Esperar el Deployment Inicial

- La base de datos se creará primero (~2-3 minutos)
- Luego el backend (~5-7 minutos)
- Finalmente el frontend (~5-7 minutos)

**Total:** ~15-20 minutos para el primer deployment

---

### Opción B: Deployment Manual (Si Blueprint no funciona)

#### 1. Crear Base de Datos PostgreSQL

1. Dashboard > **"New +"** > **"PostgreSQL"**
2. Configurar:
   - **Name**: `botdo-db`
   - **Database**: `botdo`
   - **User**: `botdo_user`
   - **Region**: Oregon (o el más cercano)
   - **Plan**: Free
3. Clic en **"Create Database"**
4. Esperar ~2-3 minutos hasta que esté "Available"

#### 2. Crear Backend (FastAPI)

1. Dashboard > **"New +"** > **"Web Service"**
2. Conectar tu repositorio
3. Configurar:
   - **Name**: `botdo-backend`
   - **Region**: Oregon
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Environment**: Docker
   - **Dockerfile Path**: `Dockerfile.prod`
   - **Plan**: Free
4. En **"Advanced"**:
   - **Health Check Path**: `/health`
5. Clic en **"Create Web Service"**

#### 3. Crear Frontend (React)

1. Dashboard > **"New +"** > **"Web Service"**
2. Conectar tu repositorio
3. Configurar:
   - **Name**: `botdo-frontend`
   - **Region**: Oregon
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Environment**: Docker
   - **Dockerfile Path**: `Dockerfile.prod`
   - **Plan**: Free
4. Clic en **"Create Web Service"**

---

## 🔐 Configuración de Variables de Entorno

### Para el Backend (botdo-backend)

1. Ve a tu servicio **botdo-backend**
2. Clic en **"Environment"** en el menú lateral
3. Agregar las siguientes variables:

#### Variables Automáticas

Render ya configuró:
- ✅ `DATABASE_URL` (conectado automáticamente desde botdo-db)

#### Variables Manuales

Agregar una por una:

```bash
# Seguridad
SECRET_KEY=<genera con: openssl rand -hex 32>
ENVIRONMENT=production

# Slack
SLACK_BOT_TOKEN=xoxb-tu-token-aqui
SLACK_SIGNING_SECRET=tu-signing-secret-aqui

# Whapi
WHAPI_API_KEY=tu-whapi-key-aqui
WHAPI_BASE_URL=https://gate.whapi.cloud

# DigitalOcean
DO_API_TOKEN=dop_v1_tu-token-aqui

# Configuración adicional
UVICORN_WORKERS=2
LOG_LEVEL=INFO
```

**Generar SECRET_KEY:**
```bash
openssl rand -hex 32
```

4. Clic en **"Save Changes"**
5. El servicio se re-deployará automáticamente

### Para el Frontend (botdo-frontend)

1. Ve a tu servicio **botdo-frontend**
2. Clic en **"Environment"**
3. Agregar:

```bash
# URL del Backend (reemplaza con tu URL real)
REACT_APP_API_URL=https://botdo-backend.onrender.com
```

**Nota**: La URL del backend la obtienes de:
- Dashboard > botdo-backend > URL mostrada arriba

4. Clic en **"Save Changes"**

---

## 🗄️ Inicializar Base de Datos

### Opción 1: Desde Render Dashboard (Recomendado)

1. Ve a **botdo-db** en el Dashboard
2. Clic en **"Connect"** > **"External Connection"**
3. Copia la cadena de conexión PSQL
4. En tu terminal local:

```bash
# Conectarse a la base de datos
psql <PEGA_LA_CADENA_DE_CONEXION_AQUI>

# Dentro de psql, ejecutar el script
\i database/render-init.sql

# Verificar tablas
\dt

# Salir
\q
```

### Opción 2: Usando el Dashboard de Render

1. Ve a **botdo-db** > **"Query"** (en el menú lateral)
2. Abre el archivo `database/render-init.sql`
3. Copia todo el contenido
4. Pégalo en el editor de queries
5. Clic en **"Run Query"**

### Opción 3: Crear Admin User (Opcional)

Después de inicializar la base de datos, crear un usuario admin:

1. Conectarse a la base de datos
2. Ejecutar el script `create_admin.py`:

```bash
# En tu terminal local, con la cadena de conexión
DATABASE_URL=<tu_database_url_aqui> python backend/create_admin.py
```

O manualmente en psql:

```sql
INSERT INTO admin_users (username, email, hashed_password, is_active)
VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5OMaiMKfcHlZm', -- password: admin123
    true
);
```

---

## ✅ Verificación del Deployment

### 1. Verificar Backend

Visita: `https://botdo-backend.onrender.com/health`

Deberías ver:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. Verificar API Docs

Visita: `https://botdo-backend.onrender.com/docs`

Deberías ver la documentación interactiva de Swagger.

### 3. Verificar Frontend

Visita: `https://botdo-frontend.onrender.com`

Deberías ver tu aplicación React cargada.

### 4. Verificar Database

```bash
# Conectarse a la base de datos
psql <tu_connection_string>

# Verificar tablas
\dt

# Verificar contenido
SELECT * FROM admin_users;
```

---

## 🔗 Configuración de Webhooks

### Slack Webhooks

1. Ve a [api.slack.com/apps](https://api.slack.com/apps)
2. Selecciona tu app
3. **Event Subscriptions** > Enable Events
4. **Request URL**: `https://botdo-backend.onrender.com/api/connectors/slack/events`
5. **Subscribe to bot events**:
   - `message.channels`
   - `message.groups`
   - `message.im`
   - `message.mpim`
6. **Save Changes**

### Whapi Webhooks

1. Ve a tu dashboard de Whapi
2. **Webhooks** > Add New
3. **URL**: `https://botdo-backend.onrender.com/api/connectors/whapi/webhook`
4. **Events**: Selecciona los eventos que necesites
5. **Save**

---

## 🐛 Troubleshooting

### Error: Service Won't Start

**Solución:**
```bash
# Ver logs
Dashboard > Service > Logs

# Verificar que las variables de entorno estén configuradas
Dashboard > Service > Environment
```

### Error: Database Connection Failed

**Solución:**
```bash
# Verificar que DATABASE_URL esté configurado
Dashboard > botdo-backend > Environment > DATABASE_URL

# Verificar que la base de datos esté running
Dashboard > botdo-db > Status: Available
```

### Error: Frontend Can't Connect to Backend

**Solución:**
```bash
# Verificar REACT_APP_API_URL
Dashboard > botdo-frontend > Environment > REACT_APP_API_URL

# Debe ser: https://botdo-backend.onrender.com
# NO http, NO localhost
```

### Service "Sleeping" (Plan Free)

En el plan free, los servicios "duermen" después de 15 minutos de inactividad.

**Soluciones:**
1. Upgrade a plan paid ($7/mes por servicio)
2. Usar un servicio de "ping" como [UptimeRobot](https://uptimerobot.com) (gratis)
3. Aceptar el delay de ~30 segundos en el primer request

### Build Fails

**Solución:**
```bash
# Verificar Dockerfile.prod existe
ls backend/Dockerfile.prod
ls frontend/Dockerfile.prod

# Verificar sintaxis Docker
docker build -f backend/Dockerfile.prod backend/
docker build -f frontend/Dockerfile.prod frontend/
```

### Database Initialization Fails

**Solución:**
```bash
# Ejecutar script manualmente
psql <connection_string> < database/render-init.sql

# O usar el Query Editor en Render Dashboard
```

---

## 💰 Costos y Planes

### Plan Free (Recomendado para Empezar)

**Incluye:**
- ✅ Backend: Gratis (con sleep después de 15 min)
- ✅ Frontend: Gratis (con sleep después de 15 min)
- ✅ PostgreSQL: Gratis por 90 días (luego $7/mes)

**Limitaciones:**
- ⏰ Services duermen después de 15 min de inactividad
- ⚡ Primer request después de sleep: ~30 segundos
- 💾 Database: 1 GB storage
- 🔄 750 horas/mes de compute

**Costo Total:** $0/mes (primeros 90 días), luego $7/mes

### Plan Starter (Recomendado para Producción)

**Incluye:**
- Backend Web Service: $7/mes
- Frontend Web Service: $7/mes
- PostgreSQL: $7/mes

**Beneficios:**
- ⚡ Sin sleep - siempre disponible
- 💪 Mejor performance
- 💾 10 GB storage en DB
- 🔄 Uptime garantizado

**Costo Total:** $21/mes

### Upgrade Individual

Puedes hacer upgrade de servicios individuales:
- Solo Backend: $7/mes (mantener frontend free)
- Solo Database: $7/mes después de 90 días

---

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
# Dashboard > Service > Logs > clic en "Live Logs"
```

### Descargar Logs

```bash
# Dashboard > Service > Logs > clic en "Download"
```

### Métricas

```bash
# Dashboard > Service > Metrics
# Ver: CPU, Memory, Requests, Response Times
```

---

## 🔄 Auto-Deploy

### Configurar Auto-Deploy

Ya está configurado con `autoDeploy: true` en `render.yaml`.

Cada vez que hagas push a `main`:
```bash
git push origin main
```

Render automáticamente:
1. Detecta el cambio
2. Hace pull del código
3. Rebuilda la imagen Docker
4. Deploya la nueva versión
5. ✅ Sin downtime (zero-downtime deployment)

### Deshabilitar Auto-Deploy

```bash
# Dashboard > Service > Settings > "Auto-Deploy" > Disable
```

---

## 🎯 Checklist Final

Antes de considerar el deployment completo:

- [ ] Backend está "Available" y responde en `/health`
- [ ] Frontend está "Available" y carga correctamente
- [ ] Database está "Available" con todas las tablas creadas
- [ ] Todas las variables de entorno están configuradas
- [ ] Admin user creado y puede hacer login
- [ ] Slack webhooks configurados y funcionando
- [ ] Whapi webhooks configurados y funcionando
- [ ] Auto-deploy habilitado
- [ ] Logs están limpios sin errores críticos

---

## 🚀 ¡Deployment Completo!

**URLs de tu aplicación:**

- 🌐 Frontend: `https://botdo-frontend.onrender.com`
- 🔌 Backend API: `https://botdo-backend.onrender.com`
- 📚 API Docs: `https://botdo-backend.onrender.com/docs`
- 🗄️ Database: Conectado internamente

---

## 📞 Soporte

Si encuentras problemas:

1. **Logs**: Revisar logs en Dashboard
2. **Status**: Verificar status de servicios
3. **Environment**: Verificar variables de entorno
4. **Render Docs**: [render.com/docs](https://render.com/docs)
5. **Community**: [community.render.com](https://community.render.com)

---

## 📚 Recursos Adicionales

- [Render Documentation](https://render.com/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Production Build](https://create-react-app.dev/docs/production-build/)

---

**¡Felicidades! Tu bot está en producción 🎉**

Para siguientes deployments, solo necesitas:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Y Render se encargará del resto automáticamente.

