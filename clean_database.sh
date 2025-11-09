#!/bin/bash

# ============================================
# BotDO Database Cleanup Script
# ============================================
# This script cleans up the database by removing all data from:
# - messages table
# - channels table
# - users table
# 
# Note: admin_users table is NOT affected
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  BotDO Database Cleanup Script${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Load environment variables from .env file
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${GREEN}✓ Loading environment variables from .env${NC}"
    export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | grep -v '^$' | xargs)
else
    echo -e "${RED}✗ Error: .env file not found!${NC}"
    echo -e "${YELLOW}  Please make sure the .env file exists in the project root.${NC}"
    exit 1
fi

# Check if required variables are set
if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ] || [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_PORT" ]; then
    echo -e "${RED}✗ Error: Required environment variables are not set!${NC}"
    echo -e "${YELLOW}  Please check your .env file contains:${NC}"
    echo -e "${YELLOW}  - POSTGRES_USER${NC}"
    echo -e "${YELLOW}  - POSTGRES_PASSWORD${NC}"
    echo -e "${YELLOW}  - POSTGRES_DB${NC}"
    echo -e "${YELLOW}  - POSTGRES_PORT${NC}"
    exit 1
fi

# Database configuration
DB_CONTAINER="botdo_db"
DB_HOST="localhost"
DB_PORT="${POSTGRES_PORT}"
DB_NAME="${POSTGRES_DB}"
DB_USER="${POSTGRES_USER}"
DB_PASSWORD="${POSTGRES_PASSWORD}"

# Check if running with --force flag
FORCE_MODE=false
if [ "$1" == "--force" ] || [ "$1" == "-f" ]; then
    FORCE_MODE=true
fi

echo ""
echo -e "${YELLOW}⚠️  WARNING: This will DELETE all data from:${NC}"
echo -e "${YELLOW}   - messages table${NC}"
echo -e "${YELLOW}   - channels table${NC}"
echo -e "${YELLOW}   - users table${NC}"
echo ""
echo -e "${GREEN}ℹ️  admin_users table will NOT be affected${NC}"
echo ""

# Ask for confirmation unless --force is used
if [ "$FORCE_MODE" = false ]; then
    read -p "Are you sure you want to continue? (yes/no): " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        echo -e "${BLUE}✓ Operation cancelled${NC}"
        exit 0
    fi
fi

echo ""
echo -e "${BLUE}Starting database cleanup...${NC}"
echo ""

# Check if database container is running
if ! docker ps | grep -q "$DB_CONTAINER"; then
    echo -e "${RED}✗ Error: Database container '$DB_CONTAINER' is not running!${NC}"
    echo -e "${YELLOW}  Please start the containers with: docker-compose up -d${NC}"
    exit 1
fi

# SQL commands to clean the database
SQL_COMMANDS="
DO \$\$
DECLARE
    messages_count INTEGER;
    channels_count INTEGER;
    users_count INTEGER;
BEGIN
    -- Get counts before deletion
    SELECT COUNT(*) INTO messages_count FROM messages;
    SELECT COUNT(*) INTO channels_count FROM channels;
    SELECT COUNT(*) INTO users_count FROM users;
    
    -- Delete data (order matters due to foreign keys)
    DELETE FROM messages;
    DELETE FROM channels;
    DELETE FROM users;
    
    -- Display results
    RAISE NOTICE '';
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Cleanup completed successfully!';
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Records deleted:';
    RAISE NOTICE '  - Messages: %', messages_count;
    RAISE NOTICE '  - Channels: %', channels_count;
    RAISE NOTICE '  - Users: %', users_count;
    RAISE NOTICE '============================================';
    RAISE NOTICE '';
END \$\$;
"

# Execute cleanup using docker exec
echo -e "${BLUE}→ Executing cleanup queries...${NC}"
echo ""

PGPASSWORD="$DB_PASSWORD" docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" <<EOF
$SQL_COMMANDS
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}✓ Database cleanup completed successfully!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "${BLUE}All test data has been removed.${NC}"
    echo -e "${BLUE}The database is now in a fresh state.${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}✗ Error during database cleanup!${NC}"
    echo -e "${RED}============================================${NC}"
    echo ""
    exit 1
fi

