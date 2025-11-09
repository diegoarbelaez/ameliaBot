# Solución: Problema de Autenticación de Base de Datos

## Problema Detectado
La contraseña de PostgreSQL tiene un valor placeholder: `your_secure_password`

## Solución

### Paso 1: Detener y eliminar todos los contenedores y volúmenes
```bash
cd /Users/diegoarbelaez/Desktop/amelia/AmeliaBot/botDO
docker-compose down -v
```

### Paso 2: Editar el archivo .env

Abre el archivo `.env` y asegúrate de tener estas variables con valores REALES:

```bash
# Database Configuration
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=botdo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=TuPasswordSeguraAqui123!

# Construir la URL completa (debe coincidir con las variables de arriba)
DATABASE_URL=postgresql://postgres:TuPasswordSeguraAqui123!@db:5432/botdo
```

**IMPORTANTE**: 
- Cambia `TuPasswordSeguraAqui123!` por una contraseña segura de tu elección
- La contraseña en `DATABASE_URL` debe ser EXACTAMENTE la misma que en `POSTGRES_PASSWORD`

### Paso 3: Volver a iniciar
```bash
docker-compose up -d
```

### Paso 4: Verificar que funciona
```bash
docker-compose logs backend | tail -20
```

Deberías ver: `✅ All required environment variables loaded successfully`

## Variables Críticas Adicionales

También necesitas configurar estas variables en tu `.env`:

```bash
# Digital Ocean AI Agent (CRÍTICO para que el bot funcione)
DIGITALOCEAN_API_KEY=dop_v1_tu_token_aqui
DIGITALOCEAN_AGENT_ID=tu_agent_id_aqui

# Secret Key (genera uno con: python3 -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=genera_uno_aleatorio_de_32_caracteres_minimo
```

