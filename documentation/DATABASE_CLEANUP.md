# Database Cleanup Script

## Descripción

Script para limpiar la base de datos BotDO y dejarla en un estado fresco para pruebas. Elimina todos los datos de mensajes, canales y usuarios, pero mantiene intacta la tabla de admin_users.

## Ubicación

```bash
./clean_database.sh
```

## Qué hace el script

El script elimina **todos los datos** de las siguientes tablas (en orden):
1. `messages` - Todos los mensajes almacenados
2. `channels` - Todos los canales registrados
3. `users` - Todos los usuarios registrados

### ⚠️ Importante
- La tabla `admin_users` NO se ve afectada
- Los usuarios administrativos y sus credenciales permanecen intactos
- El script respeta las relaciones de foreign keys

## Requisitos previos

1. Los contenedores Docker deben estar corriendo:
```bash
docker-compose up -d
```

2. El archivo `.env` debe existir en la raíz del proyecto con las variables:
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DB`
   - `POSTGRES_PORT`

## Uso

### Modo Interactivo (con confirmación)

```bash
./clean_database.sh
```

El script pedirá confirmación antes de ejecutar:
```
⚠️  WARNING: This will DELETE all data from:
   - messages table
   - channels table
   - users table

ℹ️  admin_users table will NOT be affected

Are you sure you want to continue? (yes/no):
```

### Modo Forzado (sin confirmación)

Para scripts de automatización o CI/CD:

```bash
./clean_database.sh --force
# o
./clean_database.sh -f
```

## Ejemplo de salida

```
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

## Solución de problemas

### Error: .env file not found
**Solución**: Asegúrate de ejecutar el script desde la raíz del proyecto donde está el archivo `.env`

### Error: Database container is not running
**Solución**: Inicia los contenedores con:
```bash
docker-compose up -d
```

### Error: Required environment variables are not set
**Solución**: Verifica que tu archivo `.env` contenga todas las variables necesarias:
```env
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=botdo
POSTGRES_PORT=5432
```

## Casos de uso

### Durante desarrollo
```bash
# Después de hacer pruebas y querer empezar de nuevo
./clean_database.sh
```

### En scripts de prueba automatizados
```bash
#!/bin/bash
# Limpiar antes de cada suite de pruebas
./clean_database.sh --force
npm test
```

### Antes de demos
```bash
# Limpiar datos de prueba antes de una demostración
./clean_database.sh
```

## Seguridad

- ✅ El script requiere confirmación explícita (a menos que uses --force)
- ✅ No afecta la tabla de admin_users
- ✅ Solo funciona si el contenedor de base de datos está corriendo
- ✅ Usa las credenciales del archivo .env de forma segura

## Notas adicionales

- El script muestra el número de registros eliminados de cada tabla
- El orden de eliminación respeta las foreign keys de la base de datos
- Después de la limpieza, la base de datos está lista para nuevas pruebas
- Los índices y triggers permanecen intactos

