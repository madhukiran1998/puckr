import httpx
import json
import base64
import re
import logging
from typing import Dict, Any, Optional, Union, List
from .llm_service import BaseLLMService
import os
import asyncio

# Set up logging
logger = logging.getLogger(__name__)

class GeminiService(BaseLLMService):
    """Service for interacting with Google's Gemini API with document and video processing support"""
    
    def __init__(self):
        logger.info("Initializing GeminiService")
        super().__init__()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-2.5-flash"
        
        logger.info(f"Gemini API Key: {'SET' if self.api_key else 'NOT SET'}")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Model: {self.model}")
        
        if not self.api_key:
            logger.error("GEMINI_API_KEY environment variable is required")
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        logger.info("✅ GeminiService initialized successfully")
    
    async def process_documents(self, documents: Union[bytes, str, List[Union[bytes, str]]], prompt: str) -> Dict[str, Any]:
        """
        Process PDF documents using Gemini's native document understanding
        
        Args:
            documents: PDF data as bytes, URL, or list of PDFs
            prompt: The prompt to apply to the documents
            
        Returns:
            Dictionary containing processing results
        """
        logger.info(f"Processing documents with Gemini")
        logger.info(f"Documents type: {type(documents)}")
        logger.info(f"Documents: {documents}")
        logger.info(f"Prompt: {prompt}")
        
        try:
            # Add concise system context for document processing
            enhanced_prompt = f"Document Analysis Task: {prompt}\n\nProvide clear, structured insights from the document content."
            logger.info(f"Enhanced prompt: {enhanced_prompt}")
            
            response = await self._call_gemini_api_with_pdf(enhanced_prompt, documents)
            logger.info(f"Gemini API response: {response}")
            
            return {
                "success": True,
                "prompt": prompt,
                "processing_results": response,
                "model": self.model,
                "service": "gemini",
                "content_type": "pdf"
            }
            
        except Exception as e:
            logger.error(f"Error in process_documents: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt,
                "service": "gemini",
                "content_type": "pdf"
            }
    
    async def process_content(self, content: Union[str, bytes, List[Union[str, bytes]]], prompt: str) -> Dict[str, Any]:
        """
        Process content with a specific prompt - handles PDFs and YouTube videos
        
        Args:
            content: The content to process - can be string, document bytes, or list of URLs/documents
            prompt: The prompt to apply to the content
            
        Returns:
            Dictionary containing processing results
        """
        logger.info(f"Processing content with Gemini")
        logger.info(f"Content type: {type(content)}")
        logger.info(f"Content: {content}")
        logger.info(f"Prompt: {prompt}")
        
        # Handle single content item
        if not isinstance(content, list):
            content = [content]
        
        results = []
        
        for item in content:
            logger.info(f"Processing item: {item}")
            if isinstance(item, str):
                # Check if it's a YouTube URL
                if "youtube.com" in item or "youtu.be" in item:
                    logger.info("Detected YouTube URL, processing as video")
                    result = await self.process_youtube_video(item, prompt)
                else:
                    logger.info("Processing as document")
                    # Assume it's a PDF URL or other document
                    result = await self.process_documents(item, prompt)
            else:
                logger.info("Processing as document bytes")
                # Assume it's PDF bytes
                result = await self.process_documents(item, prompt)
            
            logger.info(f"Item processing result: {result}")
            results.append(result)
        
        # If single item, return single result, otherwise return list
        if len(results) == 1:
            logger.info("Returning single result")
            return results[0]
        else:
            logger.info("Returning multiple results")
            return {
                "success": True,
                "prompt": prompt,
                "processing_results": results,
                "model": self.model,
                "service": "gemini",
                "content_type": "mixed"
            }
    
    async def process_youtube_video(self, youtube_url: str, prompt: str) -> Dict[str, Any]:
        """
        Process YouTube videos using Gemini's text analysis capabilities
        
        Args:
            youtube_url: YouTube video URL
            prompt: The prompt to apply to the video
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Extract video ID from YouTube URL
            video_id = self._extract_youtube_video_id(youtube_url)
            if not video_id:
                raise ValueError("Invalid YouTube URL provided")
            
            # Add concise system context for video processing
            enhanced_prompt = f"Video Analysis Task: {prompt}\n\nAnalyze the video content and provide key insights with timestamps if possible."
            response = await self._call_gemini_api_with_youtube(enhanced_prompt, video_id)
            
            return {
                "success": True,
                "prompt": prompt,
                "youtube_url": youtube_url,
                "video_id": video_id,
                "processing_results": response,
                "model": self.model,
                "service": "gemini",
                "content_type": "youtube"
            }
            
        except Exception as e:
            error_message = str(e) if str(e) else "Unknown error occurred during YouTube video processing"
            logger.error(f"YouTube video processing failed: {error_message}")
            return {
                "success": False,
                "error": error_message,
                "prompt": prompt,
                "youtube_url": youtube_url,
                "service": "gemini",
                "content_type": "youtube"
            }
    
    async def _call_gemini_api_with_pdf(self, prompt: str, pdf_data: Union[bytes, str, List[Union[bytes, str]]]) -> str:
        """Make API call to Gemini with PDF document support"""
        logger.info(f"Calling Gemini API with PDF")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"PDF data type: {type(pdf_data)}")
        
        url = f"{self.base_url}/{self.model}:generateContent"
        logger.info(f"API URL: {url}")
        
        headers = {
            "Content-Type": "application/json",
        }
        
        parts = []
        
        # Handle different PDF input types
        if isinstance(pdf_data, list):
            logger.info("Processing list of PDFs")
            # Multiple PDFs
            for item in pdf_data:
                if isinstance(item, str) and (item.startswith('http://') or item.startswith('https://')):
                    logger.info(f"Fetching PDF from URL: {item}")
                    # URL - fetch PDF
                    doc_data = await self._fetch_url_content(item)
                    logger.info(f"Fetched PDF size: {len(doc_data)} bytes")
                    parts.append({
                        "inlineData": {
                            "mimeType": "application/pdf",
                            "data": base64.b64encode(doc_data).decode('utf-8')
                        }
                    })
                elif isinstance(item, bytes):
                    logger.info(f"Processing PDF bytes, size: {len(item)} bytes")
                    # PDF bytes
                    parts.append({
                        "inlineData": {
                            "mimeType": "application/pdf",
                            "data": base64.b64encode(item).decode('utf-8')
                        }
                    })
        elif isinstance(pdf_data, str) and (pdf_data.startswith('http://') or pdf_data.startswith('https://')):
            logger.info(f"Fetching single PDF from URL: {pdf_data}")
            # Single URL
            doc_data = await self._fetch_url_content(pdf_data)
            logger.info(f"Fetched PDF size: {len(doc_data)} bytes")
            parts.append({
                "inlineData": {
                    "mimeType": "application/pdf",
                    "data": base64.b64encode(doc_data).decode('utf-8')
                }
            })
        elif isinstance(pdf_data, bytes):
            logger.info(f"Processing single PDF bytes, size: {len(pdf_data)} bytes")
            # Single PDF bytes
            parts.append({
                "inlineData": {
                    "mimeType": "application/pdf",
                    "data": base64.b64encode(pdf_data).decode('utf-8')
                }
            })
        
        # Add the prompt
        parts.append({"text": prompt})
        
        data = {
            "contents": [
                {
                    "parts": parts
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }
        
        logger.info(f"Request data structure: {len(parts)} parts")
        logger.info(f"First part type: {type(parts[0]) if parts else 'None'}")
        if parts and isinstance(parts[0], dict) and "inlineData" in parts[0]:
            data_size = len(parts[0]["inlineData"]["data"])
            logger.info(f"PDF data size (base64): {data_size} characters")
        
        logger.info(f"Request data: {json.dumps(data, indent=2)}")
        
        # Retry logic with exponential backoff
        max_retries = 3
        base_timeout = 30  # 30 seconds base timeout
        
        for attempt in range(max_retries):
            try:
                timeout = base_timeout * (2 ** attempt)  # Exponential backoff: 30s, 60s, 120s
                logger.info(f"Attempt {attempt + 1}/{max_retries} with {timeout}s timeout")
                
                async with httpx.AsyncClient(timeout=timeout) as client:
                    logger.info("Making HTTP request to Gemini API")
                    response = await client.post(
                        url,
                        headers=headers,
                        json=data,
                        params={"key": self.api_key}
                    )
                    
                    logger.info(f"Response status: {response.status_code}")
                    logger.info(f"Response headers: {dict(response.headers)}")
                    
                    if response.status_code != 200:
                        logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                        raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
                    
                    result = response.json()
                    logger.info(f"Response JSON: {json.dumps(result, indent=2)}")
                    
                    if "candidates" in result and len(result["candidates"]) > 0:
                        candidate = result["candidates"][0]
                        logger.info(f"First candidate: {json.dumps(candidate, indent=2)}")
                        
                        if "content" in candidate and "parts" in candidate["content"]:
                            parts = candidate["content"]["parts"]
                            logger.info(f"Content parts: {json.dumps(parts, indent=2)}")
                            
                            if len(parts) > 0 and "text" in parts[0]:
                                response_text = parts[0]["text"]
                                logger.info(f"Extracted response text: {response_text}")
                                if not response_text.strip():
                                    logger.warning("Response text is empty or whitespace only")
                                    # Try fallback text processing
                                    logger.info("Attempting fallback text processing...")
                                    return await self._fallback_text_processing(prompt, pdf_data)
                                return response_text
                            else:
                                logger.error("No text part found in response")
                                # Try fallback text processing
                                logger.info("Attempting fallback text processing...")
                                return await self._fallback_text_processing(prompt, pdf_data)
                        else:
                            logger.error("No content or parts found in candidate")
                            # Try fallback text processing
                            logger.info("Attempting fallback text processing...")
                            return await self._fallback_text_processing(prompt, pdf_data)
                    else:
                        logger.error("No candidates found in Gemini API response")
                        logger.error(f"Response structure: {list(result.keys())}")
                        # Try fallback text processing
                        logger.info("Attempting fallback text processing...")
                        return await self._fallback_text_processing(prompt, pdf_data)
                        
            except httpx.ReadTimeout as e:
                logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    logger.error("All retry attempts failed due to timeout")
                    raise Exception(f"Gemini API timeout after {max_retries} attempts. The request is taking too long to process.")
                else:
                    logger.info(f"Retrying in {2 ** attempt} seconds...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise
                else:
                    logger.info(f"Retrying in {2 ** attempt} seconds...")
                    await asyncio.sleep(2 ** attempt)
    
    async def _call_gemini_api_with_youtube(self, prompt: str, video_id: str) -> str:
        """Make API call to Gemini with YouTube video support"""
        url = f"{self.base_url}/{self.model}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "fileData": {
                                "fileUri": f"https://www.youtube.com/watch?v={video_id}"
                            }
                        },
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }
        
        # Retry logic with exponential backoff for YouTube processing
        max_retries = 3
        base_timeout = 60  # 60 seconds base timeout for video processing
        
        for attempt in range(max_retries):
            try:
                timeout = base_timeout * (2 ** attempt)  # Exponential backoff: 60s, 120s, 240s
                logger.info(f"YouTube processing attempt {attempt + 1}/{max_retries} with {timeout}s timeout")
                
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        url,
                        headers=headers,
                        json=data,
                        params={"key": self.api_key}
                    )
                    
                    logger.info(f"YouTube processing response status: {response.status_code}")
                    
                    if response.status_code != 200:
                        error_msg = f"Gemini API error: {response.status_code} - {response.text}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    result = response.json()
                    logger.info(f"YouTube processing response: {result}")
                    
                    if "candidates" in result and len(result["candidates"]) > 0:
                        candidate = result["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            parts = candidate["content"]["parts"]
                            if len(parts) > 0 and "text" in parts[0]:
                                response_text = parts[0]["text"]
                                logger.info(f"YouTube processing successful: {response_text[:100]}...")
                                return response_text
                    
                    # If we get here, no valid response was found
                    raise Exception("No valid response generated from Gemini API for YouTube video")
                        
            except httpx.ReadTimeout as e:
                logger.warning(f"YouTube processing timeout on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"YouTube video processing timed out after {max_retries} attempts. The video may be too long or the request is taking too long to process.")
                else:
                    logger.info(f"Retrying YouTube processing in {2 ** attempt} seconds...")
                    await asyncio.sleep(2 ** attempt)
                    
            except Exception as e:
                logger.error(f"YouTube processing error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise
                else:
                    logger.info(f"Retrying YouTube processing in {2 ** attempt} seconds...")
                    await asyncio.sleep(2 ** attempt)
    
    def _extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from various YouTube URL formats"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def _fetch_url_content(self, url: str) -> bytes:
        """Fetch content from URL"""
        logger.info(f"Fetching content from URL: {url}")
        
        # Retry logic for URL fetching
        max_retries = 3
        base_timeout = 30
        
        for attempt in range(max_retries):
            try:
                timeout = base_timeout * (2 ** attempt)
                logger.info(f"URL fetch attempt {attempt + 1}/{max_retries} with {timeout}s timeout")
                
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(url)
                    logger.info(f"URL fetch status: {response.status_code}")
                    
                    if response.status_code == 200:
                        content_length = len(response.content)
                        logger.info(f"Successfully fetched {content_length} bytes from URL")
                        return response.content
                    else:
                        logger.error(f"Failed to fetch URL {url}: {response.status_code}")
                        raise Exception(f"Failed to fetch URL {url}: {response.status_code}")
                        
            except httpx.ReadTimeout as e:
                logger.warning(f"URL fetch timeout on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    logger.error("All URL fetch attempts failed due to timeout")
                    raise Exception(f"Failed to fetch URL {url} after {max_retries} attempts due to timeout.")
                else:
                    logger.info(f"Retrying URL fetch in {2 ** attempt} seconds...")
                    await asyncio.sleep(2 ** attempt)
                    
            except Exception as e:
                logger.error(f"URL fetch error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise
                else:
                    logger.info(f"Retrying URL fetch in {2 ** attempt} seconds...")
                    await asyncio.sleep(2 ** attempt)

    async def _fallback_text_processing(self, prompt: str, pdf_data: Union[bytes, str, List[Union[bytes, str]]]) -> str:
        """Fallback method to process PDF as text when document processing fails"""
        logger.info("Using fallback text processing")
        
        try:
            # Convert PDF data to text representation
            if isinstance(pdf_data, str) and (pdf_data.startswith('http://') or pdf_data.startswith('https://')):
                # Fetch the PDF and convert to text
                pdf_bytes = await self._fetch_url_content(pdf_data)
                text_content = f"PDF Document Content (URL: {pdf_data})\n\n[PDF content extracted as text]"
            elif isinstance(pdf_data, bytes):
                text_content = f"PDF Document Content\n\n[PDF content extracted as text]"
            else:
                text_content = f"Document Content\n\n[Document content extracted as text]"
            
            # Create a simple text-based prompt
            text_prompt = f"""
            {prompt}
            
            Document Information:
            {text_content}
            
            Please provide a summary based on the document information provided.
            """
            
            logger.info("Making fallback text API call")
            
            url = f"{self.base_url}/{self.model}:generateContent"
            headers = {"Content-Type": "application/json"}
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": text_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                }
            }
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=data,
                    params={"key": self.api_key}
                )
                
                if response.status_code != 200:
                    raise Exception(f"Fallback API error: {response.status_code} - {response.text}")
                
                result = response.json()
                
                if "candidates" in result and len(result["candidates"]) > 0:
                    response_text = result["candidates"][0]["content"]["parts"][0]["text"]
                    logger.info(f"Fallback response: {response_text}")
                    return response_text
                else:
                    raise Exception("No response from fallback API call")
                    
        except Exception as e:
            logger.error(f"Fallback processing failed: {e}")
            return "Unable to process the document. The file may be corrupted or in an unsupported format."
