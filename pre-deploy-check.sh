#!/bin/bash

# Script de Verificación Pre-Deployment para Render
# Ejecuta este script antes de hacer push a producción

set -e

echo "🔍 Verificando configuración para deployment en Render..."
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores
SUCCESS=0
WARNINGS=0
ERRORS=0

# Función para verificar archivos
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 existe"
        ((SUCCESS++))
    else
        echo -e "${RED}✗${NC} $1 NO EXISTE"
        ((ERRORS++))
    fi
}

# Función para verificar directorios
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 existe"
        ((SUCCESS++))
    else
        echo -e "${RED}✗${NC} $1 NO EXISTE"
        ((ERRORS++))
    fi
}

echo "1️⃣  Verificando archivos de configuración de Render..."
check_file "render.yaml"
check_file "render.env.example"
check_file "RENDER_QUICK_START.md"
check_file "documentation/RENDER_DEPLOYMENT.md"
echo ""

echo "2️⃣  Verificando Dockerfiles de producción..."
check_file "backend/Dockerfile.prod"
check_file "frontend/Dockerfile.prod"
check_file "frontend/nginx.conf"
echo ""

echo "3️⃣  Verificando scripts de base de datos..."
check_file "database/init.sql"
check_file "database/render-init.sql"
echo ""

echo "4️⃣  Verificando estructura del proyecto..."
check_dir "backend/app"
check_dir "frontend/src"
check_file "backend/requirements.txt"
check_file "frontend/package.json"
echo ""

echo "5️⃣  Verificando archivos críticos del backend..."
check_file "backend/app/main.py"
check_file "backend/app/database.py"
check_file "backend/app/models.py"
check_file "backend/app/schemas.py"
echo ""

echo "6️⃣  Verificando archivos críticos del frontend..."
check_file "frontend/src/App.jsx"
check_file "frontend/src/index.js"
check_file "frontend/public/index.html"
echo ""

echo "7️⃣  Verificando que .env NO esté en el repositorio..."
if [ -f ".env" ]; then
    if git ls-files --error-unmatch .env 2>/dev/null; then
        echo -e "${RED}✗${NC} ¡PELIGRO! .env está en el repositorio"
        echo "   Ejecuta: git rm --cached .env"
        ((ERRORS++))
    else
        echo -e "${GREEN}✓${NC} .env existe pero NO está en el repositorio"
        ((SUCCESS++))
    fi
else
    echo -e "${YELLOW}⚠${NC}  .env no existe (esto es OK si usarás variables de Render)"
    ((WARNINGS++))
fi
echo ""

echo "8️⃣  Verificando .gitignore..."
if [ -f ".gitignore" ]; then
    if grep -q "\.env" .gitignore; then
        echo -e "${GREEN}✓${NC} .env está en .gitignore"
        ((SUCCESS++))
    else
        echo -e "${YELLOW}⚠${NC}  .env NO está en .gitignore (agrégalo)"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}✗${NC} .gitignore NO EXISTE"
    ((ERRORS++))
fi
echo ""

echo "9️⃣  Verificando scripts de build..."
if grep -q '"build"' frontend/package.json; then
    echo -e "${GREEN}✓${NC} Script 'build' existe en package.json"
    ((SUCCESS++))
else
    echo -e "${RED}✗${NC} Script 'build' NO EXISTE en package.json"
    ((ERRORS++))
fi
echo ""

echo "🔟  Verificando Git status..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Repositorio Git inicializado"
    ((SUCCESS++))
    
    # Verificar si hay cambios sin commit
    if [[ -n $(git status -s) ]]; then
        echo -e "${YELLOW}⚠${NC}  Tienes cambios sin commit:"
        git status -s
        ((WARNINGS++))
    else
        echo -e "${GREEN}✓${NC} No hay cambios sin commit"
        ((SUCCESS++))
    fi
else
    echo -e "${RED}✗${NC} NO es un repositorio Git"
    ((ERRORS++))
fi
echo ""

# Resumen final
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 RESUMEN DE VERIFICACIÓN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ Exitosos: ${SUCCESS}${NC}"
echo -e "${YELLOW}⚠ Advertencias: ${WARNINGS}${NC}"
echo -e "${RED}✗ Errores: ${ERRORS}${NC}"
echo ""

# Verificación de Docker (opcional)
echo "🐳 Verificando Docker (opcional)..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker está instalado"
    
    # Intentar build local
    read -p "¿Deseas probar build local de Docker? (s/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "Building backend..."
        if docker build -f backend/Dockerfile.prod -t botdo-backend-test backend/; then
            echo -e "${GREEN}✓${NC} Backend build exitoso"
        else
            echo -e "${RED}✗${NC} Backend build falló"
            ((ERRORS++))
        fi
        
        echo "Building frontend..."
        if docker build -f frontend/Dockerfile.prod -t botdo-frontend-test frontend/; then
            echo -e "${GREEN}✓${NC} Frontend build exitoso"
        else
            echo -e "${RED}✗${NC} Frontend build falló"
            ((ERRORS++))
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC}  Docker no está instalado (no es necesario para Render)"
fi
echo ""

# Recomendaciones finales
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 RECOMENDACIONES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ HAY ERRORES CRÍTICOS${NC}"
    echo "   Corrige los errores antes de hacer deployment"
    echo ""
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  HAY ADVERTENCIAS${NC}"
    echo "   Puedes continuar, pero revisa las advertencias"
    echo ""
    echo "Pasos sugeridos:"
    echo "1. Revisa y corrige las advertencias"
    echo "2. git add ."
    echo "3. git commit -m 'Ready for Render deployment'"
    echo "4. git push origin main"
    echo "5. Sigue la guía en RENDER_QUICK_START.md"
    echo ""
    exit 0
else
    echo -e "${GREEN}✅ TODO LISTO PARA DEPLOYMENT${NC}"
    echo ""
    echo "Próximos pasos:"
    echo "1. git add ."
    echo "2. git commit -m 'Ready for Render deployment'"
    echo "3. git push origin main"
    echo "4. Ve a render.com y sigue RENDER_QUICK_START.md"
    echo ""
    echo "📚 Documentación completa: documentation/RENDER_DEPLOYMENT.md"
    echo ""
    exit 0
fi

