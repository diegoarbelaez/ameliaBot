"""
Digital Ocean Agent Client for BotDO.
Handles communication with Digital Ocean AI Agent API.
"""
import httpx
import os
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DigitalOceanClient:
    """
    Client for interacting with Digital Ocean AI Agent.
    """
    
    def __init__(self):
        """
        Initialize Digital Ocean client with credentials from environment.
        """
        self.api_key = os.getenv("DIGITALOCEAN_API_KEY")
        self.agent_id = os.getenv("DIGITALOCEAN_AGENT_ID")
        self.api_url = os.getenv("DIGITALOCEAN_API_URL", "https://api.digitalocean.com/v2")
        
        if not self.api_key:
            raise ValueError("DIGITALOCEAN_API_KEY not set in environment")
        if not self.agent_id:
            raise ValueError("DIGITALOCEAN_AGENT_ID not set in environment")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def send_to_agent(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = 1000,
        temperature: Optional[float] = 0.7
    ) -> str:
        """
        Send conversation to Digital Ocean Agent and get response.
        
        Args:
            messages: List of messages in OpenAI format
                [{"role": "user", "content": "..."}, ...]
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0.0 to 1.0)
            
        Returns:
            Agent's response text
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        # Construct the API endpoint for the agent
        # If api_url already contains .agents.do-ai.run, it's a direct agent URL
        if ".agents.do-ai.run" in self.api_url:
            # Direct agent URL - use OpenAI-compatible endpoint
            endpoint = f"{self.api_url}/api/v1/chat/completions"
        else:
            # Standard API URL - use full path
            endpoint = f"{self.api_url}/ai/agents/{self.agent_id}/chat"
        
        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        logger.info("🌊 Enviando request a Digital Ocean Agent...")
        logger.info(f"   Endpoint: {endpoint}")
        logger.info(f"   Número de mensajes: {len(messages)}")
        logger.info(f"   Max tokens: {max_tokens}, Temperature: {temperature}")
        logger.info(f"   Mensajes:")
        for i, msg in enumerate(messages[-3:], 1):  # Log últimos 3 mensajes
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100]  # Primeros 100 chars
            logger.info(f"      [{i}] {role}: {content}...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info("📡 Realizando llamada HTTP a Digital Ocean...")
                
                response = await client.post(
                    endpoint,
                    headers=self.headers,
                    json=payload
                )
                
                logger.info(f"📥 Respuesta recibida - Status Code: {response.status_code}")
                
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"📋 Estructura de respuesta: {list(data.keys())}")
                
                # Extract the response text from the API response
                # The exact structure may vary based on DO API
                # Adjust this based on actual API response format
                if "choices" in data and len(data["choices"]) > 0:
                    agent_response = data["choices"][0]["message"]["content"]
                    logger.info(f"✅ Respuesta extraída de 'choices[0].message.content'")
                    logger.info(f"   Respuesta ({len(agent_response)} chars): {agent_response[:100]}...")
                    return agent_response
                elif "response" in data:
                    agent_response = data["response"]
                    logger.info(f"✅ Respuesta extraída de 'response'")
                    logger.info(f"   Respuesta ({len(agent_response)} chars): {agent_response[:100]}...")
                    return agent_response
                elif "message" in data:
                    agent_response = data["message"]
                    logger.info(f"✅ Respuesta extraída de 'message'")
                    logger.info(f"   Respuesta ({len(agent_response)} chars): {agent_response[:100]}...")
                    return agent_response
                else:
                    logger.error(f"❌ Formato de respuesta inesperado de Digital Ocean")
                    logger.error(f"   Estructura recibida: {data}")
                    return "Lo siento, hubo un error al procesar tu solicitud."
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Error HTTP de Digital Ocean Agent:")
            logger.error(f"   Status Code: {e.response.status_code}")
            logger.error(f"   Response: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"❌ Error de conexión con Digital Ocean Agent:")
            logger.error(f"   Error: {str(e)}")
            logger.error(f"   Endpoint: {endpoint}")
            raise
        except Exception as e:
            logger.error(f"❌ Error inesperado con Digital Ocean Agent:")
            logger.error(f"   Error: {str(e)}", exc_info=True)
            raise
    
    async def health_check(self) -> bool:
        """
        Check if the Digital Ocean Agent is accessible.
        
        Returns:
            True if agent is accessible, False otherwise
        """
        try:
            endpoint = f"{self.api_url}/ai/agents/{self.agent_id}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers
                )
                response.raise_for_status()
                return True
                
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

