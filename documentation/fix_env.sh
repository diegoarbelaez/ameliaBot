#!/bin/bash

# Script para ayudar a configurar las credenciales de la base de datos

echo "================================"
echo "🔧 Configurador de Credenciales"
echo "================================"
echo ""

# Verificar que .env existe
if [ ! -f ".env" ]; then
    echo "❌ Error: .env no encontrado"
    exit 1
fi

echo "Este script te ayudará a configurar las credenciales correctas."
echo ""
echo "📋 Configuración actual de PostgreSQL:"
echo ""
grep -E "^POSTGRES_|^DATABASE_URL" .env || echo "No se encontraron variables POSTGRES"
echo ""

# Generar una contraseña aleatoria sugerida
SUGGESTED_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-20)

echo "================================"
echo "💡 SUGERENCIAS:"
echo "================================"
echo ""
echo "1. Para PostgreSQL:"
echo "   POSTGRES_USER=postgres"
echo "   POSTGRES_PASSWORD=$SUGGESTED_PASSWORD"
echo "   POSTGRES_DB=botdo"
echo "   POSTGRES_HOST=db"
echo "   POSTGRES_PORT=5432"
echo ""
echo "   DATABASE_URL=postgresql://postgres:$SUGGESTED_PASSWORD@db:5432/botdo"
echo ""
echo "2. Abre el archivo .env en tu editor:"
echo "   nano .env"
echo "   o"
echo "   code .env"
echo ""
echo "3. Actualiza las variables de PostgreSQL con los valores de arriba"
echo ""
echo "4. También verifica estas variables críticas:"
echo "   - DIGITALOCEAN_API_KEY (debe empezar con 'dop_')"
echo "   - DIGITALOCEAN_AGENT_ID"
echo "   - SECRET_KEY (mínimo 32 caracteres)"
echo ""
echo "5. Después de editar, ejecuta:"
echo "   docker-compose up -d"
echo ""
echo "================================"
echo ""
read -p "¿Quieres que copie la configuración sugerida al portapapeles? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    CONFIG="# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$SUGGESTED_PASSWORD
POSTGRES_DB=botdo
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql://postgres:$SUGGESTED_PASSWORD@db:5432/botdo"
    
    echo "$CONFIG" | pbcopy 2>/dev/null || echo "$CONFIG" | xclip -selection clipboard 2>/dev/null || echo "No se pudo copiar al portapapeles, pero aquí está la configuración:"
    echo ""
    echo "$CONFIG"
    echo ""
    echo "✅ Configuración lista para pegar en tu .env"
fi

echo ""
echo "📖 Para más detalles, revisa: FIX_DATABASE.md"

