import httpx
import json
from typing import Dict, Any, Optional, Union, List
from .llm_service import BaseLLMService
import os

class PerplexityService(BaseLLMService):
    """Service for interacting with Perplexity API"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai"
        self.model = "llama-3.1-sonar-small-128k-online"
        
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable is required")
    
    async def process_content(self, content: Union[str, bytes, List[Union[str, bytes]]], prompt: str) -> Dict[str, Any]:
        """
        Process content with a specific prompt using Perplexity API
        
        Args:
            content: The content to process - can be string, document bytes, or list of URLs/documents
            prompt: The prompt to apply to the content
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Concise system prompt for Perplexity
            system_prompt = "You are a content analysis assistant. Provide clear, well-structured insights based on the provided content. Focus on key information and practical takeaways."
            
            # Convert content to string for Perplexity API
            if isinstance(content, list):
                content_text = "\n\n".join([str(item) for item in content])
            elif isinstance(content, bytes):
                content_text = content.decode('utf-8', errors='ignore')
            else:
                content_text = str(content)
            
            user_prompt = f"""
            Content to process:
            {content_text}
            
            Prompt: {prompt}
            """
            
            response = await self._call_perplexity_api(system_prompt, user_prompt, search=False)
            
            return {
                "success": True,
                "prompt": prompt,
                "processing_results": response,
                "model": self.model,
                "service": "perplexity"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt,
                "service": "perplexity"
            }
    
    async def _call_perplexity_api(self, system_prompt: str, user_prompt: str, search: bool = False) -> str:
        """Make API call to Perplexity"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": False
        }
        
        # Add search parameters if search is enabled
        if search:
            data["search"] = True
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception("No response generated from Perplexity API")
