# Guía de Logs - BotDO

## Descripción

Este documento describe todos los logs que genera el sistema para facilitar el debugging y monitoreo del bot.

## Logs por Proceso

### 1. Inicio del Sistema

```
✅ All required environment variables loaded successfully
```

### 2. Verificación de Canal Slack

**Endpoint:** `GET /canales/slack/health`

```
✅ Canal Slack conectado: bot_id=U01234567, team=Tu Team
```

o en caso de error:

```
❌ Canal Slack no conectado: [error details]
```

### 3. Recepción de Mensaje

**Cuando llega un evento de Slack:**

```
📩 Mensaje recibido de Slack: user=U01234567, channel=C01234567
```

**Si es el challenge de verificación de URL:**

```
🔐 Slack URL verification challenge
```

**Si la firma es inválida:**

```
❌ Firma de Slack inválida
```

### 4. Guardado de Mensaje

**Cuando se guarda el mensaje del usuario en la BD:**

```
💾 Mensaje guardado en BD: slack/C01234567
```

### 5. Comunicación con Digital Ocean

**Cuando se envía la conversación al agente:**

```
🤖 Enviando a Digital Ocean Agent: 5 mensajes
```

**Cuando se recibe respuesta exitosa:**

```
✅ Respuesta recibida de Digital Ocean Agent
```

**En caso de errores:**

```
❌ Error HTTP de Digital Ocean: 404
❌ Error de conexión con Digital Ocean
❌ Error inesperado con Digital Ocean Agent
❌ Formato de respuesta inesperado de Digital Ocean
```

### 6. Guardado de Respuesta del Bot

**Cuando se guarda la respuesta en la BD:**

```
💾 Respuesta del bot guardada en BD
```

### 7. Envío a Slack

**Cuando se envía la respuesta al usuario:**

```
📤 Enviando respuesta a Slack: channel=C01234567
```

**En caso de error al enviar:**

```
❌ Error enviando mensaje a Slack: [error details]
```

### 8. Errores Generales

**Error en el procesamiento del bot:**

```
❌ Error en procesamiento del bot: [error details]
```

**Error procesando el app_mention:**

```
❌ Error procesando app_mention: [error details]
```

**Errores al obtener información de Slack:**

```
❌ Error obteniendo info de usuario Slack
❌ Error obteniendo info de canal Slack
```

## Flujo Completo Exitoso

Cuando todo funciona correctamente, verás esta secuencia de logs:

```
2025-11-07 10:30:00 - app.routers.connectors.slack - INFO - 📩 Mensaje recibido de Slack: user=U01234567, channel=C01234567
2025-11-07 10:30:00 - app.routers.bot - INFO - 💾 Mensaje guardado en BD: slack/C01234567
2025-11-07 10:30:00 - app.routers.bot - INFO - 🤖 Enviando a Digital Ocean Agent: 5 mensajes
2025-11-07 10:30:02 - app.routers.bot - INFO - ✅ Respuesta recibida de Digital Ocean Agent
2025-11-07 10:30:02 - app.routers.bot - INFO - 💾 Respuesta del bot guardada en BD
2025-11-07 10:30:02 - app.routers.connectors.slack - INFO - 📤 Enviando respuesta a Slack: channel=C01234567
```

## Tiempo Estimado

- **Recepción → Guardado:** < 100ms
- **Guardado → Envío a DO:** < 50ms
- **Envío a DO → Respuesta:** 1-3 segundos (depende del agente)
- **Respuesta → Guardado:** < 100ms
- **Guardado → Envío a Slack:** < 500ms

**Total:** ~2-4 segundos desde que el usuario envía el mensaje hasta que ve la respuesta.

## Ver Logs en Desarrollo

### Usando uvicorn directamente

```bash
cd backend
uvicorn app.main:app --reload
```

Los logs se mostrarán en la consola automáticamente.

### Usando Docker

```bash
# Ver logs en tiempo real
docker-compose logs -f backend

# Ver últimas 100 líneas
docker-compose logs --tail=100 backend

# Ver logs desde un timestamp
docker-compose logs --since="2025-11-07T10:00:00" backend
```

## Niveles de Log

El sistema usa tres niveles:

- **INFO** (🟢): Operaciones normales y exitosas
- **WARNING** (🟡): Advertencias que no detienen el flujo
- **ERROR** (🔴): Errores que requieren atención

## Filtrar Logs

### Ver solo logs de Slack

```bash
docker-compose logs -f backend | grep "slack"
```

### Ver solo logs de Digital Ocean

```bash
docker-compose logs -f backend | grep "Digital Ocean"
```

### Ver solo errores

```bash
docker-compose logs -f backend | grep "ERROR"
```

### Ver flujo completo de un mensaje

```bash
docker-compose logs -f backend | grep -E "📩|💾|🤖|✅|📤"
```

## Troubleshooting con Logs

### El bot no responde

Busca en los logs:

1. ¿Llega el mensaje? → Busca `📩 Mensaje recibido`
2. ¿Se guarda? → Busca `💾 Mensaje guardado`
3. ¿Se envía a DO? → Busca `🤖 Enviando a Digital Ocean`
4. ¿Responde DO? → Busca `✅ Respuesta recibida`
5. ¿Se envía a Slack? → Busca `📤 Enviando respuesta`

### Error de firma inválida

Si ves `❌ Firma de Slack inválida`:

- Verificar `SLACK_SIGNING_SECRET` en `.env`
- Verificar que la URL en Slack sea correcta
- Verificar que no haya proxy intermedio modificando headers

### Error de Digital Ocean

Si ves errores de DO:

- Verificar `DIGITALOCEAN_API_KEY`
- Verificar `DIGITALOCEAN_AGENT_ID`
- Verificar conectividad de red
- Revisar status del agente en Digital Ocean

### Canal no conectado

Si ves `❌ Canal Slack no conectado`:

- Verificar `SLACK_BOT_TOKEN`
- Verificar que el bot esté instalado en el workspace
- Verificar permisos del bot

## Monitoreo en Producción

Para producción, considera:

1. **Agregar log rotation** para evitar archivos muy grandes
2. **Configurar alertas** para logs de ERROR
3. **Usar herramientas de agregación** como ELK Stack, Grafana Loki, etc.
4. **Configurar métricas** para tiempos de respuesta

## Ejemplo de Script de Monitoreo

```bash
#!/bin/bash
# monitor_bot.sh

echo "Monitoreando logs del bot..."
echo "Presiona Ctrl+C para detener"
echo ""

docker-compose logs -f backend | while read line; do
    # Colorear según tipo de log
    if echo "$line" | grep -q "📩"; then
        echo -e "\033[0;34m$line\033[0m"  # Azul
    elif echo "$line" | grep -q "✅"; then
        echo -e "\033[0;32m$line\033[0m"  # Verde
    elif echo "$line" | grep -q "❌"; then
        echo -e "\033[0;31m$line\033[0m"  # Rojo
    elif echo "$line" | grep -q "🤖"; then
        echo -e "\033[0;35m$line\033[0m"  # Magenta
    elif echo "$line" | grep -q "📤"; then
        echo -e "\033[0;36m$line\033[0m"  # Cyan
    else
        echo "$line"
    fi
done
```

Guardar como `monitor_bot.sh`, dar permisos y ejecutar:

```bash
chmod +x monitor_bot.sh
./monitor_bot.sh
```

## Configuración Avanzada de Logging

Para modificar el nivel de log o formato, editar `backend/app/main.py`:

```python
# Cambiar nivel a DEBUG para ver más detalles
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar aquí
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

Niveles disponibles:
- `DEBUG` - Muy verboso, incluye todos los detalles
- `INFO` - Normal (recomendado)
- `WARNING` - Solo advertencias y errores
- `ERROR` - Solo errores
- `CRITICAL` - Solo errores críticos

---

Con esta guía podrás hacer debugging efectivo del sistema y entender exactamente qué está pasando en cada paso del flujo del bot.

