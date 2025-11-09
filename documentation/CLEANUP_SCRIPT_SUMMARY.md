# Database Cleanup Script - Resumen de Implementación

## 📋 Descripción General

Se ha creado un script shell completo para limpiar la base de datos de BotDO, eliminando datos de prueba de forma rápida y segura.

## ✅ Archivos Creados

### 1. Script Principal
- **Ubicación**: `clean_database.sh` (raíz del proyecto)
- **Permisos**: Ejecutable (chmod +x aplicado)
- **Tamaño**: 4.6 KB

### 2. Documentación
- `documentation/DATABASE_CLEANUP.md` (3.8 KB) - Guía completa del script
- `documentation/TESTING_WORKFLOW.md` (5.0 KB) - Flujo de trabajo de pruebas
- `QUICK_COMMANDS.md` (3.3 KB) - Referencia rápida de comandos
- `README.md` - Actualizado con referencia al nuevo script

## 🎯 Funcionalidades Implementadas

### Script clean_database.sh

✅ **Modo Interactivo**
- Solicita confirmación antes de ejecutar
- Muestra advertencias claras sobre qué se eliminará
- Colorización de mensajes para mejor UX

✅ **Modo Forzado (--force/-f)**
- Ejecución sin confirmación
- Ideal para scripts automatizados
- Útil para CI/CD pipelines

✅ **Validaciones de Seguridad**
- Verifica existencia del archivo .env
- Valida variables de entorno requeridas
- Confirma que el contenedor de BD está corriendo
- Protege tabla admin_users (no se elimina)

✅ **Operaciones de Base de Datos**
- Elimina datos de tabla `messages`
- Elimina datos de tabla `channels`
- Elimina datos de tabla `users`
- Respeta foreign keys (orden correcto de eliminación)
- Muestra contador de registros eliminados

✅ **Manejo de Errores**
- Detecta si el contenedor no está corriendo
- Valida configuración antes de ejecutar
- Mensajes de error claros y descriptivos
- Exit codes apropiados

## 📊 Tablas Afectadas

| Tabla | Acción | Razón |
|-------|--------|-------|
| `messages` | ✅ ELIMINA | Datos de prueba de mensajes |
| `channels` | ✅ ELIMINA | Canales de prueba |
| `users` | ✅ ELIMINA | Usuarios de prueba |
| `admin_users` | ❌ MANTIENE | Usuarios administrativos del sistema |

## 🚀 Uso

### Básico (con confirmación)
```bash
./clean_database.sh
```

### Automatizado (sin confirmación)
```bash
./clean_database.sh --force
```

### En un script de pruebas
```bash
#!/bin/bash
./clean_database.sh --force
# ... ejecutar pruebas ...
./clean_database.sh --force
```

## 🔒 Características de Seguridad

1. **Confirmación requerida por defecto** - Previene eliminaciones accidentales
2. **No afecta admin_users** - Los usuarios administrativos permanecen intactos
3. **Validación de entorno** - Verifica configuración antes de ejecutar
4. **Contenedor debe estar activo** - No puede ejecutarse si Docker está detenido
5. **Uso de variables de entorno** - Lee credenciales de .env de forma segura

## 📝 Requisitos Previos

✅ Docker y Docker Compose instalados
✅ Contenedores de BotDO corriendo (`docker-compose up -d`)
✅ Archivo `.env` configurado correctamente
✅ Variables de entorno requeridas:
   - POSTGRES_USER
   - POSTGRES_PASSWORD
   - POSTGRES_DB
   - POSTGRES_PORT

## 🎨 Características de UX

- **Colorización**: Usa colores para diferenciar tipos de mensajes
  - 🔵 Azul: Información
  - 🟢 Verde: Éxito
  - 🟡 Amarillo: Advertencias
  - 🔴 Rojo: Errores

- **Feedback claro**: Muestra exactamente cuántos registros se eliminaron de cada tabla

- **Progreso visible**: Indica qué está haciendo en cada paso

## 📚 Documentación Asociada

1. **DATABASE_CLEANUP.md**
   - Guía completa del script
   - Ejemplos de uso
   - Solución de problemas
   - Casos de uso comunes

2. **TESTING_WORKFLOW.md**
   - Flujos de trabajo recomendados
   - Scripts de automatización
   - Consultas SQL útiles
   - Buenas prácticas

3. **QUICK_COMMANDS.md**
   - Referencia rápida de comandos
   - Atajos de desarrollo
   - Comandos de debugging
   - Snippets útiles

## 🧪 Ejemplo de Salida

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

NOTICE:  ============================================
NOTICE:  Cleanup completed successfully!
NOTICE:  ============================================
NOTICE:  Records deleted:
NOTICE:    - Messages: 45
NOTICE:    - Channels: 3
NOTICE:    - Users: 12
NOTICE:  ============================================

============================================
✓ Database cleanup completed successfully!
============================================

All test data has been removed.
The database is now in a fresh state.
```

## 🔧 Integración con Flujo de Desarrollo

### Durante desarrollo local
```bash
# Limpiar antes de pruebas
./clean_database.sh --force

# Realizar pruebas
# ...

# Limpiar después
./clean_database.sh --force
```

### En scripts de CI/CD
```yaml
# GitHub Actions example
- name: Clean database
  run: ./clean_database.sh --force

- name: Run tests
  run: npm test
```

## 💡 Tips y Mejores Prácticas

1. **Usa --force en scripts**: Para automatización, siempre usa el modo forzado
2. **Limpia antes de cada test suite**: Garantiza estado limpio
3. **Verifica antes de demos**: Limpia datos de desarrollo antes de presentaciones
4. **No elimines admin_users**: El script los protege automáticamente
5. **Revisa los logs**: Siempre verifica el contador de registros eliminados

## 🐛 Troubleshooting

### "Database container is not running"
```bash
docker-compose up -d
./clean_database.sh
```

### ".env file not found"
```bash
# Asegúrate de ejecutar desde la raíz del proyecto
cd /path/to/botDO
./clean_database.sh
```

### "Required environment variables are not set"
```bash
# Valida tu .env
python backend/validate_env.py
```

## ✨ Beneficios

✅ **Ahorra tiempo** - No más consultas SQL manuales
✅ **Menos errores** - Elimina en el orden correcto respetando foreign keys
✅ **Seguro** - Confirmación y validaciones múltiples
✅ **Documentado** - Guías completas y ejemplos
✅ **Fácil de usar** - Interfaz simple e intuitiva
✅ **Automatizable** - Modo --force para scripts

## 📊 Estadísticas

- **Líneas de código**: ~180 líneas
- **Tiempo de ejecución**: < 2 segundos
- **Tablas afectadas**: 3 de 4 (admin_users protegida)
- **Documentación**: 4 archivos, ~12 KB total
- **Modos de operación**: 2 (interactivo y forzado)

## 🎯 Casos de Uso Principales

1. **Testing local** - Limpiar entre ejecuciones de test
2. **Desarrollo** - Reset rápido durante desarrollo de features
3. **Demos** - Preparar ambiente antes de demostraciones
4. **CI/CD** - Integración en pipelines automáticos
5. **Debugging** - Estado limpio para reproducir bugs

## 🔄 Actualizaciones Futuras Sugeridas

Posibles mejoras futuras:
- [ ] Opción para hacer backup antes de limpiar
- [ ] Modo verbose con más detalles
- [ ] Opción para limpiar solo una tabla específica
- [ ] Estadísticas antes/después de la limpieza
- [ ] Integración con scripts de seed de datos de prueba
- [ ] Logging a archivo de las operaciones realizadas

---

**Fecha de creación**: 9 de Noviembre, 2025
**Versión**: 1.0
**Estado**: ✅ Producción

