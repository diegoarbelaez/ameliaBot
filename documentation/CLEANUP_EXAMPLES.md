# Database Cleanup Script - Ejemplos de Uso

## 🎯 Ejemplos Prácticos

### Ejemplo 1: Primera vez usando el script

```bash
$ ./clean_database.sh

============================================
  BotDO Database Cleanup Script
============================================

✓ Loading environment variables from .env

⚠️  WARNING: This will DELETE all data from:
   - messages table
   - channels table
   - users table

ℹ️  admin_users table will NOT be affected

Are you sure you want to continue? (yes/no): yes

Starting database cleanup...

→ Executing cleanup queries...

NOTICE:  
NOTICE:  ============================================
NOTICE:  Cleanup completed successfully!
NOTICE:  ============================================
NOTICE:  Records deleted:
NOTICE:    - Messages: 45
NOTICE:    - Channels: 3
NOTICE:    - Users: 12
NOTICE:  ============================================
NOTICE:  

============================================
✓ Database cleanup completed successfully!
============================================

All test data has been removed.
The database is now in a fresh state.
```

### Ejemplo 2: Uso con modo --force (sin confirmación)

```bash
$ ./clean_database.sh --force

============================================
  BotDO Database Cleanup Script
============================================

✓ Loading environment variables from .env

⚠️  WARNING: This will DELETE all data from:
   - messages table
   - channels table
   - users table

ℹ️  admin_users table will NOT be affected

Starting database cleanup...

→ Executing cleanup queries...

NOTICE:  
NOTICE:  ============================================
NOTICE:  Cleanup completed successfully!
NOTICE:  ============================================
NOTICE:  Records deleted:
NOTICE:    - Messages: 0
NOTICE:    - Channels: 0
NOTICE:    - Users: 0
NOTICE:  ============================================
NOTICE:  

============================================
✓ Database cleanup completed successfully!
============================================

All test data has been removed.
The database is now in a fresh state.
```

### Ejemplo 3: Cancelar la operación

```bash
$ ./clean_database.sh

============================================
  BotDO Database Cleanup Script
============================================

✓ Loading environment variables from .env

⚠️  WARNING: This will DELETE all data from:
   - messages table
   - channels table
   - users table

ℹ️  admin_users table will NOT be affected

Are you sure you want to continue? (yes/no): no

✓ Operation cancelled
```

### Ejemplo 4: Error - Contenedor no está corriendo

```bash
$ ./clean_database.sh

============================================
  BotDO Database Cleanup Script
============================================

✓ Loading environment variables from .env

⚠️  WARNING: This will DELETE all data from:
   - messages table
   - channels table
   - users table

ℹ️  admin_users table will NOT be affected

Are you sure you want to continue? (yes/no): yes

Starting database cleanup...

✗ Error: Database container 'botdo_db' is not running!
  Please start the containers with: docker-compose up -d
```

**Solución:**
```bash
$ docker-compose up -d
Creating network "botdo_botdo_network" with driver "bridge"
Creating volume "botdo_postgres_data" with default driver
Creating botdo_db ... done
Creating botdo_backend ... done
Creating botdo_frontend ... done

$ ./clean_database.sh --force
# Ahora funciona correctamente
```

### Ejemplo 5: Error - Archivo .env no encontrado

```bash
$ ./clean_database.sh

============================================
  BotDO Database Cleanup Script
============================================

✗ Error: .env file not found!
  Please make sure the .env file exists in the project root.
```

**Solución:**
```bash
$ cp .env.example .env
$ nano .env  # Editar con tus credenciales
$ python backend/validate_env.py  # Validar configuración
$ ./clean_database.sh
# Ahora funciona
```

### Ejemplo 6: Integración en script de pruebas

**test_suite.sh:**
```bash
#!/bin/bash

echo "🧪 Starting BotDO Test Suite"
echo "=============================="
echo ""

# 1. Limpiar base de datos
echo "📁 Step 1: Cleaning database..."
./clean_database.sh --force
if [ $? -ne 0 ]; then
    echo "❌ Failed to clean database"
    exit 1
fi
echo "✅ Database cleaned"
echo ""

# 2. Ejecutar pruebas de backend
echo "🔧 Step 2: Running backend tests..."
docker exec botdo_backend pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "❌ Backend tests failed"
    exit 1
fi
echo "✅ Backend tests passed"
echo ""

# 3. Verificar que se crearon datos
echo "📊 Step 3: Verifying test data..."
docker exec -it botdo_db psql -U postgres -d botdo -c "
SELECT 
    'Messages' as table_name, COUNT(*) as count FROM messages
    UNION ALL
    SELECT 'Users', COUNT(*) FROM users
    UNION ALL
    SELECT 'Channels', COUNT(*) FROM channels;
"
echo ""

# 4. Limpiar después de las pruebas
echo "🧹 Step 4: Cleaning up test data..."
./clean_database.sh --force
echo "✅ Cleanup completed"
echo ""

echo "=============================="
echo "✅ Test suite completed successfully!"
```

**Ejecutar:**
```bash
$ chmod +x test_suite.sh
$ ./test_suite.sh

🧪 Starting BotDO Test Suite
==============================

📁 Step 1: Cleaning database...
✅ Database cleaned

🔧 Step 2: Running backend tests...
✅ Backend tests passed

📊 Step 3: Verifying test data...
 table_name | count 
------------+-------
 Messages   |    10
 Users      |     3
 Channels   |     2
(3 rows)

🧹 Step 4: Cleaning up test data...
✅ Cleanup completed

==============================
✅ Test suite completed successfully!
```

### Ejemplo 7: Verificar datos antes de limpiar

```bash
# Ver cuántos datos hay antes de limpiar
$ docker exec -it botdo_db psql -U postgres -d botdo -c "
SELECT 
    'Messages' as table_name, COUNT(*) as count FROM messages
    UNION ALL
    SELECT 'Users', COUNT(*) FROM users
    UNION ALL
    SELECT 'Channels', COUNT(*) FROM channels;
"

 table_name | count 
------------+-------
 Messages   |    45
 Users      |    12
 Channels   |     3
(3 rows)

# Limpiar
$ ./clean_database.sh --force

# Verificar que está limpio
$ docker exec -it botdo_db psql -U postgres -d botdo -c "
SELECT 
    'Messages' as table_name, COUNT(*) as count FROM messages
    UNION ALL
    SELECT 'Users', COUNT(*) FROM users
    UNION ALL
    SELECT 'Channels', COUNT(*) FROM channels;
"

 table_name | count 
------------+-------
 Messages   |     0
 Users      |     0
 Channels   |     0
(3 rows)

✅ Base de datos limpia!
```

### Ejemplo 8: Uso en desarrollo iterativo

```bash
# Ciclo de desarrollo típico

# 1. Empezar con BD limpia
$ ./clean_database.sh --force

# 2. Hacer cambios en el código
$ code backend/app/routers/messages.py

# 3. Reiniciar backend
$ docker-compose restart backend

# 4. Probar manualmente enviando mensajes desde Slack
# ... enviar algunos mensajes de prueba ...

# 5. Verificar que se guardaron correctamente
$ docker exec -it botdo_db psql -U postgres -d botdo -c "
SELECT message_id, channel, LEFT(message_text, 40) as preview 
FROM messages 
ORDER BY timestamp DESC 
LIMIT 5;
"

# 6. Si algo salió mal, limpiar y probar de nuevo
$ ./clean_database.sh --force

# 7. Repetir el ciclo hasta que funcione
```

### Ejemplo 9: Preparar demo

```bash
# Antes de una demostración importante

# 1. Asegurarse de que todo está limpio
$ ./clean_database.sh --force

# 2. Verificar que los servicios están corriendo bien
$ docker-compose ps
       Name                     Command               State           Ports
----------------------------------------------------------------------------------
botdo_backend    uvicorn app.main:app --hos ...   Up      0.0.0.0:8000->8000/tcp
botdo_db         docker-entrypoint.sh postgres    Up      0.0.0.0:5432->5432/tcp
botdo_frontend   docker-entrypoint.sh npm start   Up      0.0.0.0:3000->3000/tcp

# 3. Verificar salud del API
$ curl http://localhost:8000/health
{"status":"healthy","timestamp":"2025-11-09T11:00:00Z"}

# 4. ¡Listo para la demo!
```

### Ejemplo 10: Script de reset completo

```bash
#!/bin/bash
# reset_everything.sh
# Reset completo del ambiente de desarrollo

echo "🔄 Full BotDO Reset"
echo "=================="
echo ""

echo "⏸️  Stopping containers..."
docker-compose down

echo "🗑️  Removing volumes..."
docker-compose down -v

echo "🏗️  Rebuilding containers..."
docker-compose up --build -d

echo "⏳ Waiting for database to be ready..."
sleep 5

echo "🧹 Cleaning database..."
./clean_database.sh --force

echo "👤 Creating admin user..."
docker exec botdo_backend python create_admin.py

echo ""
echo "=================="
echo "✅ Reset complete!"
echo ""
echo "Access points:"
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/docs"
```

### Ejemplo 11: Monitoreo durante pruebas

```bash
# Terminal 1: Ver logs en tiempo real
$ docker-compose logs -f backend

# Terminal 2: Ejecutar ciclo de pruebas
$ ./clean_database.sh --force
$ # Realizar pruebas...
$ ./clean_database.sh --force

# Terminal 3: Monitorear BD
$ watch -n 2 'docker exec botdo_db psql -U postgres -d botdo -c "SELECT COUNT(*) FROM messages;"'
```

### Ejemplo 12: Verificación post-limpieza

```bash
# Script para verificar que la limpieza fue exitosa
$ docker exec -it botdo_db psql -U postgres -d botdo <<EOF
-- Verificar que las tablas objetivo están vacías
SELECT 'Messages' as table_name, COUNT(*) as records FROM messages;
SELECT 'Users' as table_name, COUNT(*) as records FROM users;
SELECT 'Channels' as table_name, COUNT(*) as records FROM channels;

-- Verificar que admin_users NO fue afectada
SELECT 'Admin Users' as table_name, COUNT(*) as records FROM admin_users;

-- Verificar integridad de tablas
\dt

-- Todo debería verse así:
--  table_name  | records 
-- -------------+---------
--  Messages    |       0
--  Users       |       0
--  Channels    |       0
--  Admin Users |       1  <-- No debe ser 0!
EOF
```

## 💡 Tips para Uso Efectivo

1. **Usa --force en scripts**: Para automatización, siempre usa modo forzado
2. **Verifica antes**: Revisa los datos antes de limpiar si es importante
3. **Combina con otros comandos**: Integra en tus flujos de trabajo
4. **Documenta tus casos**: Crea scripts para casos de uso recurrentes
5. **Revisa los logs**: Siempre verifica el contador de registros eliminados

## ⚠️ Advertencias Importantes

- ❌ **NO** ejecutes en producción sin backup
- ❌ **NO** uses --force si no estás seguro
- ✅ **SÍ** verifica que estás en el ambiente correcto
- ✅ **SÍ** mantén backups de datos importantes
- ✅ **SÍ** usa en desarrollo y testing sin miedo

