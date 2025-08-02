import logging
from typing import Dict, Any, Optional
from ..service.llm.llm_service import BaseLLMService
from ..service.llm.gemini_service import GeminiService
from ..service.llm.grok_service import GrokService
from ..service.llm.perplexity_service import PerplexityService
from ..models import UserResponse
from ..db.supabase_client import supabase

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AIHelperService:
    """Simple helper service that fetches content from DB and processes with appropriate LLM"""
    
    def __init__(self):
        logger.info("Initializing AIHelperService")
        # Direct service instances - no factory needed
        try:
            self.gemini_service = GeminiService()
            logger.info("✅ GeminiService initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize GeminiService: {e}")
            raise
            
        try:
            self.grok_service = GrokService()
            logger.info("✅ GrokService initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize GrokService: {e}")
            raise
            
        try:
            self.perplexity_service = PerplexityService()
            logger.info("✅ PerplexityService initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize PerplexityService: {e}")
            raise
            
        logger.info("✅ All AI services initialized successfully")
    
    def _get_llm_service(self, content_type: str):
        """Get appropriate LLM service based on content type"""
        logger.info(f"Getting LLM service for content type: {content_type}")
        
        if content_type in ["pdf", "word", "document"]:
            logger.info("Selected GeminiService for document")
            return self.gemini_service  # Best for documents
        elif content_type in ["youtube", "video"]:
            logger.info("Selected GeminiService for video")
            return self.gemini_service  # Only Gemini supports video
        elif content_type in ["twitter", "x", "x_post"]:
            logger.info("Selected GrokService for X/Twitter content")
            return self.grok_service  # Only grok supports x data with live search
        elif content_type in ["reddit", "blog"]:
            logger.info("Selected PerplexityService for web content")
            return self.perplexity_service  # Good for web content
        else:
            logger.info("Selected GeminiService as default")
            return self.gemini_service  # Default
    
    def _enhance_prompt_with_context(self, original_prompt: str, content_type: str, content_name: str = None) -> str:
        """Enhance the user prompt with content type context for better LLM understanding"""
        logger.info(f"Enhancing prompt for content type: {content_type}")
        
        # Content type specific context
        context_map = {
            "pdf": "You are analyzing a PDF document. Focus on extracting key information, main points, and insights from the document structure and content.",
            "word": "You are analyzing a Word document. Extract key information, main points, and insights from the document content.",
            "document": "You are analyzing a document. Extract key information, main points, and insights from the content.",
            "youtube": "You are analyzing a YouTube video. Focus on the video content, key topics discussed, and main insights from the visual and audio content.",
            "video": "You are analyzing a video. Focus on the visual and audio content, key topics, and main insights.",
            "twitter": "You are analyzing X (Twitter) content using Grok's live search capabilities. Focus on the key messages, context, engagement, related discussions, and broader implications from the social media content.",
            "x": "You are analyzing X (Twitter) content using Grok's live search capabilities. Focus on the key messages, context, engagement, related discussions, and broader implications from the social media content.",
            "x_post": "You are analyzing X (Twitter) content using Grok's live search capabilities. Focus on the key messages, context, engagement, related discussions, and broader implications from the social media content.",
            "reddit": "You are analyzing Reddit content. Focus on the discussion, key points, and community insights from the forum content.",
            "blog": "You are analyzing a blog post or article. Focus on the main arguments, key insights, and important information from the written content."
        }
        
        # Get context for content type
        context = context_map.get(content_type.lower(), "You are analyzing content. Provide clear, concise insights based on the provided information.")
        
        # Build enhanced prompt
        enhanced_prompt = f"{context}\n\nUser Request: {original_prompt}"
        
        # Add content name if available
        if content_name:
            enhanced_prompt = f"{context}\n\nContent: {content_name}\n\nUser Request: {original_prompt}"
        
        logger.info(f"Enhanced prompt: {enhanced_prompt}")
        return enhanced_prompt
    
    async def process_file(self, file_id: str, prompt: str, user: UserResponse) -> Dict[str, Any]:
        """Process a file by ID"""
        logger.info(f"Processing file with ID: {file_id}")
        logger.info(f"User ID: {user.id}")
        logger.info(f"Original prompt: {prompt}")
        
        try:
            # Fetch file from DB
            logger.info("Fetching file from database...")
            result = supabase.table("files").select("*").eq("id", file_id).eq("user_id", str(user.id)).single().execute()
            
            if not result.data:
                logger.error("File not found in database")
                return {"success": False, "error": "File not found"}
            
            file_data = result.data
            logger.info(f"File data retrieved: {file_data}")
            
            file_url = file_data["file_url"]
            file_type = file_data["file_type"]
            file_name = file_data.get("name", "Unknown file")
            
            logger.info(f"Processing file: {file_name}")
            logger.info(f"File type: {file_type}")
            logger.info(f"File URL: {file_url}")
            
            # Determine LLM based on file type
            llm_service = self._get_llm_service(file_type)
            logger.info(f"Selected LLM service: {llm_service.__class__.__name__}")
            
            # Enhance prompt with content type context
            enhanced_prompt = self._enhance_prompt_with_context(prompt, file_type, file_name)
            
            # Process with LLM
            logger.info("Calling LLM service...")
            result = await llm_service.process_content(file_url, enhanced_prompt)
            logger.info(f"LLM result: {result}")
            
            # Add context
            result["file_id"] = file_id
            result["user_id"] = str(user.id)
            result["content_type"] = file_type
            result["original_prompt"] = prompt  # Keep original prompt for reference
            
            logger.info("File processing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in process_file: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Provide more specific error messages
            error_message = str(e)
            if "timeout" in error_message.lower():
                return {"success": False, "error": "The AI service is taking too long to process your file. Please try again with a smaller file or try later."}
            elif "api" in error_message.lower() and "key" in error_message.lower():
                return {"success": False, "error": "AI service configuration error. Please contact support."}
            elif "fetch" in error_message.lower() and "url" in error_message.lower():
                return {"success": False, "error": "Unable to access the file. Please check if the file is still available."}
            elif "not found" in error_message.lower():
                return {"success": False, "error": "File not found in the database."}
            else:
                return {"success": False, "error": f"File processing failed: {error_message}"}
    
    async def process_link(self, link_id: str, prompt: str, user: UserResponse) -> Dict[str, Any]:
        """Process a link by ID"""
        logger.info(f"Processing link with ID: {link_id}")
        
        try:
            # Fetch link from DB
            result = supabase.table("links").select("*").eq("id", link_id).eq("user_id", str(user.id)).single().execute()
            
            if not result.data:
                return {"success": False, "error": "Link not found"}
            
            link_data = result.data
            link_url = link_data["url"]
            link_type = link_data["link_type"]
            link_title = link_data.get("title", "Unknown link")
            
            # Determine LLM based on link type
            llm_service = self._get_llm_service(link_type)
            
            # Enhance prompt with content type context
            enhanced_prompt = self._enhance_prompt_with_context(prompt, link_type, link_title)
            
            # Process with LLM
            result = await llm_service.process_content(link_url, enhanced_prompt)
            
            # Add context
            result["link_id"] = link_id
            result["user_id"] = str(user.id)
            result["content_type"] = link_type
            result["original_prompt"] = prompt  # Keep original prompt for reference
            
            return result
            
        except Exception as e:
            logger.error(f"Error in process_link: {str(e)}")
            return {"success": False, "error": f"Link processing failed: {str(e)}"} 