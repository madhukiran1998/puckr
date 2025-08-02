import httpx
import json
import base64
from typing import Dict, Any, Optional, Union, List
from .llm_service import BaseLLMService
import os

class GrokService(BaseLLMService):
    """Simplified service for interacting with xAI's Grok API with basic live search"""
    
    def __init__(self):
        super().__init__()
        
        self.api_key = os.getenv("GROK_API_KEY")
        self.base_url = "https://api.x.ai/v1"
        self.model = "grok-4"
        
        if not self.api_key:
            raise ValueError("GROK_API_KEY environment variable is required")
    
    async def process_content(self, content: Union[str, bytes, List[Union[str, bytes]]], prompt: str) -> Dict[str, Any]:
        """
        Process content with a simple prompt using Grok API
        
        Args:
            content: The content to process - can be string, document bytes, or list of URLs/documents
            prompt: The prompt to apply to the content
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Simple system prompt
            system_prompt = "You are Grok, an AI assistant. Provide clear, insightful analysis based on the provided content."
            
            # Extract URL from content if it's a string
            url = None
            if isinstance(content, str):
                if "twitter.com" in content or "x.com" in content:
                    url = content
                elif content.startswith('http'):
                    url = content
            
            # Use simple API call with basic live search
            response = await self._call_simple_api(system_prompt, prompt, url)
            
            return {
                "success": True,
                "prompt": prompt,
                "processing_results": response,
                "model": self.model,
                "service": "grok"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt,
                "service": "grok"
            }
    
    async def _call_simple_api(self, system_prompt: str, user_prompt: str, url: Optional[str] = None) -> str:
        """Make a simple API call to Grok with basic live search"""
        
        # Retry logic for timeout errors
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                return await self._make_api_call(system_prompt, user_prompt, url, attempt)
            except Exception as e:
                if "timeout" in str(e).lower() and attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise e
    
    async def _make_api_call(self, system_prompt: str, user_prompt: str, url: Optional[str] = None, attempt: int = 0) -> str:
        """Make the actual API call with retry logic"""
        
        api_url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Build messages
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # Add content context if URL is provided
        if url:
            user_prompt = f"Content URL: {url}\n\nUser Request: {user_prompt}"
        
        messages.append({
            "role": "user",
            "content": user_prompt
        })
        
        # Simple data structure that we know works
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": False
        }
        
        # Add basic live search if it's an X URL
        if url and ("twitter.com" in url or "x.com" in url):
            data["search_parameters"] = {
                "mode": "auto",
                "sources": [{"type": "x"}],
                "return_citations": True,
                "max_search_results": 3
            }
        
        try:
            # Use a longer timeout for live search requests
            timeout_duration = 180.0 if "search_parameters" in data else 120.0
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=data,
                    timeout=timeout_duration
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    raise Exception(f"Grok API error: {response.status_code} - {error_text}")
                
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    
                    # Add usage information if available
                    if "usage" in result:
                        usage_info = result["usage"]
                        if "num_sources_used" in usage_info:
                            content += f"\n\n[Analysis used {usage_info['num_sources_used']} data sources]"
                    
                    return content
                else:
                    raise Exception("No response generated from Grok API")
                    
        except httpx.TimeoutException as e:
            raise Exception(f"Grok API timeout: The request took too long to complete. Please try again with a simpler prompt or try later when the service is less busy.")
        except httpx.RequestError as e:
            raise Exception(f"Grok API request error: {str(e)}")
        except Exception as e:
            raise
    
    async def _fetch_url_content(self, url: str) -> str:
        """Fetch content from URL and return as text"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=60.0)
                
                if response.status_code == 200:
                    return response.text
                else:
                    raise Exception(f"Failed to fetch URL {url}: {response.status_code}")
        except httpx.TimeoutException as e:
            raise Exception(f"Timeout fetching URL {url}: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to fetch URL {url}: {str(e)}")
    
    # Legacy methods for compatibility
    async def _call_grok_api_with_live_search(self, system_prompt: str, user_prompt: str, x_url: str) -> str:
        """Legacy method - now calls simple API"""
        return await self._call_simple_api(system_prompt, user_prompt, x_url)
    
    async def _call_grok_api_with_content(self, system_prompt: str, user_prompt: str, content: Optional[Union[str, bytes, list]] = None) -> str:
        """Legacy method - now calls simple API"""
        url = content if isinstance(content, str) else None
        return await self._call_simple_api(system_prompt, user_prompt, url)
    
    async def _call_grok_api(self, system_prompt: str, user_prompt: str) -> str:
        """Legacy method - now calls simple API"""
        return await self._call_simple_api(system_prompt, user_prompt, None)
