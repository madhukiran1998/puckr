from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
import os
from dotenv import load_dotenv

load_dotenv()

class BaseLLMService(ABC):
    """Base class for LLM services with common functionality"""
    
    def __init__(self):
        self.api_key = None
        self.base_url = None
        self.model = None
    
    @abstractmethod
    async def process_content(self, content: Union[str, bytes, List[Union[str, bytes]]], prompt: str) -> Dict[str, Any]:
        """
        Process content with a specific prompt
        
        Args:
            content: The content to process - can be string, document bytes, or list of URLs/documents
            prompt: The prompt to apply to the content
            
        Returns:
            Dictionary containing processing results
        """
        pass
    
    def get_service_name(self) -> str:
        """Get the name of this service"""
        return self.__class__.__name__.lower().replace('service', '')
    
    def get_model_name(self) -> str:
        """Get the model name being used"""
        return self.model or "unknown"
