# 📊 Guía de Logging y Monitoreo

## 🎯 Logs Mejorados - Ahora Activos

El sistema de logging ha sido mejorado significativamente para proporcionar visibilidad completa del flujo de datos desde Slack hasta Digital Ocean y de vuelta.

---

## 📺 Cómo Ver los Logs en Tiempo Real

### Opción 1: Ver todos los logs del backend

```bash
docker-compose logs -f backend
```

### Opción 2: Ver solo logs recientes (últimas 50 líneas)

```bash
docker-compose logs -f --tail=50 backend
```

### Opción 3: Ver logs con timestamps

```bash
docker-compose logs -f -t backend
```

### Opción 4: Filtrar logs específicos

```bash
# Solo logs de Slack
docker-compose logs -f backend | grep slack

# Solo logs de Digital Ocean
docker-compose logs -f backend | grep "Digital Ocean"

# Solo errores
docker-compose logs -f backend | grep -E "ERROR|❌"

# Solo mensajes exitosos
docker-compose logs -f backend | grep -E "✅|SUCCESS"
```

---

## 🔍 Qué Información Verás Ahora

### 1. **Eventos de Slack Entrantes**

Cuando Slack envía un evento, verás:

```
============================================================
📨 NUEVO EVENTO DE SLACK RECIBIDO
🔐 Verificando firma de Slack (timestamp: 1699522800)
✅ Firma de Slack verificada correctamente
📋 Tipo de evento principal: event_callback
📨 Event callback recibido - tipo: app_mention
📝 Datos del evento: {'type': 'app_mention', 'user': 'U123...', ...}
📩 APP_MENTION detectado:
   👤 Usuario: U09RFADKFH8
   📺 Canal: C123456789
   💬 Texto: @BotDO hola, ¿cómo estás?
```

### 2. **Procesamiento del Mensaje**

Verás todo el flujo de procesamiento:

```
🔄 Iniciando procesamiento de app_mention...
📝 Texto original: '<@U123> hola, ¿cómo estás?'
🧹 Texto limpio (sin mención del bot): 'hola, ¿cómo estás?'
👤 Obteniendo información del usuario U09RFADKFH8...
✅ Usuario: Diego Arbelaez (diego@example.com)
📺 Obteniendo información del canal C123456789...
✅ Canal: #general
📦 Preparando request para el bot...
🤖 Enviando mensaje al endpoint del bot para procesamiento...
   Plataforma: slack
   Usuario: Diego Arbelaez
   Canal: #general
   Mensaje: 'hola, ¿cómo estás?'
```

### 3. **Procesamiento Interno del Bot**

```
============================================================
🤖 BOT PROCESS REQUEST - INICIO
📊 Request info:
   Plataforma: slack
   Usuario: Diego Arbelaez (ID: U09RFADKFH8)
   Canal: #general (ID: C123456789)
   Mensaje: 'hola, ¿cómo estás?'
🔧 Inicializando servicios...
✅ Servicios inicializados
👤 Obteniendo o creando usuario en BD...
✅ Usuario obtenido: DB ID=1
📺 Obteniendo o creando canal en BD...
✅ Canal obtenido: DB ID=1
💾 Guardando mensaje del usuario en BD...
✅ Mensaje guardado: DB ID=42
📚 Obteniendo historial de conversación (últimos 20 mensajes)...
✅ Historial obtenido: 5 mensajes
🔄 Formateando mensajes a formato OpenAI...
➕ Mensaje actual agregado al contexto
✅ Total de mensajes en contexto: 6
```

### 4. **Comunicación con Digital Ocean**

```
🌊 Enviando conversación a Digital Ocean Agent...
🌊 Enviando request a Digital Ocean Agent...
   Endpoint: https://api.digitalocean.com/v2/ai/agents/agent-123/chat
   Número de mensajes: 6
   Max tokens: 1000, Temperature: 0.7
   Mensajes:
      [1] user: mensaje anterior...
      [2] assistant: respuesta anterior...
      [3] user: hola, ¿cómo estás?...
📡 Realizando llamada HTTP a Digital Ocean...
📥 Respuesta recibida - Status Code: 200
📋 Estructura de respuesta: ['choices', 'usage', 'model']
✅ Respuesta extraída de 'choices[0].message.content'
   Respuesta (142 chars): ¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?...
✅ Respuesta recibida de Digital Ocean Agent (142 chars)
```

### 5. **Respuesta al Usuario**

```
💾 Guardando respuesta del bot en BD...
✅ Respuesta guardada: DB ID=43
🎉 BOT PROCESS REQUEST - COMPLETADO EXITOSAMENTE
============================================================
✅ Respuesta recibida del bot (success=True)
📤 Enviando respuesta a Slack:
   Canal: C123456789
   Thread: 1699522800.123456
   Respuesta: '¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?...'
✅ Mensaje enviado exitosamente a Slack
✅ Evento app_mention procesado correctamente
============================================================
```

---

## ❌ Logs de Errores

Si algo falla, verás información detallada:

### Error de Autenticación Slack

```
❌ Firma de Slack inválida - REQUEST RECHAZADO
```

### Error de Digital Ocean

```
❌ Error HTTP de Digital Ocean Agent:
   Status Code: 401
   Response: {"error": "unauthorized", "message": "Invalid API key"}
```

### Error de Base de Datos

```
❌ ERROR PROCESANDO MENSAJE:
   Error: (psycopg2.OperationalError) server closed the connection
   Tipo: OperationalError
```

---

## 🎨 Emoji Guía

Para facilitar la lectura de los logs:

| Emoji | Significado |
|-------|-------------|
| 📨 | Evento recibido |
| 🔐 | Verificación de seguridad |
| ✅ | Operación exitosa |
| ❌ | Error |
| ⚠️  | Advertencia |
| 🔄 | Procesamiento en curso |
| 👤 | Información de usuario |
| 📺 | Información de canal |
| 💬 | Contenido del mensaje |
| 🧹 | Limpieza/procesamiento de texto |
| 📦 | Preparación de datos |
| 🤖 | Procesamiento del bot |
| 📚 | Historial/contexto |
| 🌊 | Digital Ocean |
| 📡 | Request HTTP |
| 📥 | Respuesta recibida |
| 💾 | Operación de base de datos |
| 📤 | Envío de mensaje |
| 🎉 | Proceso completado exitosamente |

---

## 🔧 Comandos Útiles

### Ver solo los mensajes del usuario

```bash
docker-compose logs -f backend | grep "💬 Texto:"
```

### Ver solo las respuestas del bot

```bash
docker-compose logs -f backend | grep "📤 Enviando respuesta"
```

### Ver el flujo completo de un mensaje

Los logs están organizados con separadores `====` para facilitar seguir cada mensaje completo.

### Guardar logs en un archivo

```bash
docker-compose logs backend > logs_$(date +%Y%m%d_%H%M%S).txt
```

### Ver logs de las últimas 2 horas

```bash
docker-compose logs backend --since 2h
```

---

## 📈 Monitoreo de Performance

### Identificar mensajes lentos

Los logs incluyen timestamps que te permiten calcular el tiempo de procesamiento:

```
2025-11-09 10:15:30 - 🤖 BOT PROCESS REQUEST - INICIO
2025-11-09 10:15:35 - 🎉 BOT PROCESS REQUEST - COMPLETADO
```

En este ejemplo, el procesamiento tomó 5 segundos.

### Verificar conexión con Digital Ocean

```bash
curl http://localhost:8000/bot/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "bot_service": "running",
  "digitalocean_agent": "connected"
}
```

---

## 🐛 Debugging

### Si no ves logs de eventos de Slack

1. Verifica que los Event Subscriptions estén configurados correctamente
2. Verifica que el bot esté invitado al canal
3. Revisa que la URL de webhook sea correcta

### Si los eventos llegan pero no se procesan

Los logs te dirán exactamente dónde falla:
- ❌ en verificación de firma → Problema con SLACK_SIGNING_SECRET
- ❌ en obtener usuario → Problema de permisos de Slack API
- ❌ en Digital Ocean → Problema con API key o Agent ID
- ❌ en base de datos → Problema de conexión a PostgreSQL

---

## 💡 Tips

1. **Mantén los logs abiertos** mientras pruebas para ver el flujo en tiempo real
2. **Usa grep** para filtrar la información que necesitas
3. **Los emojis** hacen más fácil escanear visualmente los logs
4. **Los separadores** (====) delimitan cada mensaje completo
5. **Guarda logs** cuando encuentres errores para análisis posterior

---

## 🚀 Próximos Pasos

Una vez que veas fluir los logs correctamente:

1. ✅ Verifica que los eventos de Slack lleguen
2. ✅ Confirma que el texto se limpie correctamente
3. ✅ Observa la comunicación con Digital Ocean
4. ✅ Valida que las respuestas lleguen al usuario

**¡Disfruta del debugging transparente!** 🎊

