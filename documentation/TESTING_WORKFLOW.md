# Testing Workflow - BotDO

## Flujo de trabajo recomendado para pruebas

### Preparación del entorno de pruebas

```bash
# 1. Iniciar los contenedores
docker-compose up -d

# 2. Verificar que todos los servicios están corriendo
docker ps --filter "name=botdo"

# 3. Limpiar la base de datos para empezar con datos frescos
./clean_database.sh --force
```

### Durante el desarrollo

#### Escenario 1: Prueba rápida de nuevas funcionalidades

```bash
# Limpiar datos de pruebas anteriores
./clean_database.sh --force

# Ejecutar tus pruebas manuales o automáticas
# ... (realizar pruebas) ...

# Verificar logs si es necesario
docker-compose logs -f backend
```

#### Escenario 2: Prueba de integración con Slack

```bash
# 1. Limpiar base de datos
./clean_database.sh --force

# 2. Enviar mensaje desde Slack
# (usar el canal de Slack configurado)

# 3. Verificar que el mensaje se guardó
docker exec -it botdo_db psql -U postgres -d botdo -c "SELECT message_id, channel, message_text FROM messages;"

# 4. Limpiar después de las pruebas
./clean_database.sh --force
```

#### Escenario 3: Prueba de integración con WhatsApp (Whapi)

```bash
# 1. Limpiar base de datos
./clean_database.sh --force

# 2. Enviar mensaje desde WhatsApp
# (usar el endpoint de Whapi)

# 3. Verificar que el mensaje se guardó
docker exec -it botdo_db psql -U postgres -d botdo -c "SELECT message_id, channel, message_text FROM messages WHERE channel='whatsapp';"

# 4. Limpiar después de las pruebas
./clean_database.sh --force
```

### Script de automatización de pruebas

Puedes crear un script personalizado para automatizar el flujo completo:

```bash
#!/bin/bash
# test_flow.sh

echo "🧪 Starting BotDO test workflow..."

# 1. Limpiar base de datos
echo "📁 Cleaning database..."
./clean_database.sh --force

# 2. Ejecutar tus tests
echo "🚀 Running tests..."
# Aquí puedes agregar tus comandos de test
# python -m pytest tests/
# npm test
# curl tests, etc.

# 3. Mostrar resultados
echo "📊 Checking results..."
docker exec -it botdo_db psql -U postgres -d botdo -c "
    SELECT 
        'Messages' as table_name, COUNT(*) as count FROM messages
    UNION ALL
    SELECT 'Channels', COUNT(*) FROM channels
    UNION ALL
    SELECT 'Users', COUNT(*) FROM users;
"

echo "✅ Test workflow completed!"
```

### Consultas útiles para verificar datos

#### Ver todos los mensajes

```bash
docker exec -it botdo_db psql -U postgres -d botdo -c "
SELECT 
    message_id,
    channel,
    direction,
    sender_type,
    LEFT(message_text, 50) as message_preview,
    timestamp
FROM messages
ORDER BY timestamp DESC
LIMIT 10;
"
```

#### Ver estadísticas por canal

```bash
docker exec -it botdo_db psql -U postgres -d botdo -c "
SELECT 
    channel,
    direction,
    COUNT(*) as message_count
FROM messages
GROUP BY channel, direction
ORDER BY channel, direction;
"
```

#### Ver usuarios registrados

```bash
docker exec -it botdo_db psql -U postgres -d botdo -c "
SELECT 
    platform,
    platform_user_id,
    display_name,
    created_at
FROM users
ORDER BY created_at DESC;
"
```

#### Ver canales activos

```bash
docker exec -it botdo_db psql -U postgres -d botdo -c "
SELECT 
    platform,
    channel_id,
    channel_name,
    is_active,
    created_at
FROM channels
ORDER BY created_at DESC;
"
```

### Comandos rápidos de mantenimiento

```bash
# Reiniciar solo el backend (después de cambios en código)
docker-compose restart backend

# Ver logs en tiempo real
docker-compose logs -f backend

# Acceder a la base de datos interactivamente
docker exec -it botdo_db psql -U postgres -d botdo

# Ver el estado de todos los contenedores
docker-compose ps

# Detener todo
docker-compose down

# Reiniciar todo desde cero (incluyendo volúmenes)
docker-compose down -v
docker-compose up --build -d
./clean_database.sh --force
```

### Buenas prácticas

1. **Siempre limpia antes de nuevas pruebas**: Evita datos residuales que puedan afectar tus tests
2. **Documenta tus casos de prueba**: Crea scripts específicos para cada escenario
3. **Verifica los logs**: Usa `docker-compose logs -f` para debugging en tiempo real
4. **Usa --force en scripts**: Para automatización, usa el modo forzado del cleanup
5. **Backup antes de cambios grandes**: Considera hacer backup de datos importantes antes de limpiezas

### Troubleshooting

#### El script de limpieza falla

```bash
# Verificar que el contenedor esté corriendo
docker ps | grep botdo_db

# Si no está corriendo, iniciarlo
docker-compose up -d db

# Verificar logs del contenedor
docker logs botdo_db
```

#### No puedo ver los datos después de las pruebas

```bash
# Verificar conexión a la base de datos
docker exec -it botdo_db psql -U postgres -d botdo -c "\dt"

# Ver si hay datos
docker exec -it botdo_db psql -U postgres -d botdo -c "SELECT COUNT(*) FROM messages;"
```

#### Los cambios en el backend no se reflejan

```bash
# Reconstruir y reiniciar el backend
docker-compose up --build -d backend

# Ver los logs para confirmar que inició correctamente
docker-compose logs -f backend
```

