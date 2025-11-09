# Debugging DigitalOcean Agent Endpoints

## Posibles endpoints que podríamos probar:

Basándose en tu `DIGITALOCEAN_API_URL`:
```
https://s7kn3cnjpuunumerprbwddod.agents.do-ai.run
```

### Opciones de endpoint:

1. **Opción actual (la que estamos probando):**
   ```
   https://s7kn3cnjpuunumerprbwddod.agents.do-ai.run/chat
   ```

2. **Con prefijo /ai:**
   ```
   https://s7kn3cnjpuunumerprbwddod.agents.do-ai.run/ai/chat
   ```

3. **Con prefijo /v1:**
   ```
   https://s7kn3cnjpuunumerprbwddod.agents.do-ai.run/v1/chat
   ```

4. **Sin /chat (endpoint raíz):**
   ```
   https://s7kn3cnjpuunumerprbwddod.agents.do-ai.run
   ```

5. **Con /completions (estilo OpenAI):**
   ```
   https://s7kn3cnjpuunumerprbwddod.agents.do-ai.run/v1/chat/completions
   ```

## Cómo probar manualmente:

```bash
# Prueba 1: /chat
curl -X POST https://s7kn3cnjpuunumerprbwddod.agents.do-ai.run/chat \
  -H "Authorization: Bearer 9WpClWEfUo5f3VytgE3_R7GEJUV5i_gJ" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "test"}],
    "max_tokens": 100
  }'

# Prueba 2: /ai/chat
curl -X POST https://s7kn3cnjpuunumerprbwddod.agents.do-ai.run/ai/chat \
  -H "Authorization: Bearer 9WpClWEfUo5f3VytgE3_R7GEJUV5i_gJ" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "test"}],
    "max_tokens": 100
  }'

# Prueba 3: /v1/chat/completions (OpenAI compatible)
curl -X POST https://s7kn3cnjpuunumerprbwddod.agents.do-ai.run/v1/chat/completions \
  -H "Authorization: Bearer 9WpClWEfUo5f3VytgE3_R7GEJUV5i_gJ" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "test"}],
    "max_tokens": 100
  }'
```

## Verificar la documentación de DigitalOcean:

https://docs.digitalocean.com/products/ai/

O en tu panel de control de DigitalOcean AI:
https://cloud.digitalocean.com/ai

