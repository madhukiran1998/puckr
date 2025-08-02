import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..helpers.ai_helper import AIHelperService
from ..models import UserResponse
from .auth_router import get_current_user

# Set up logging
logger = logging.getLogger(__name__)

ai_router = APIRouter()
ai_helper = AIHelperService()

# Request Models
class ProcessFileRequest(BaseModel):
    file_id: str
    prompt: str

class ProcessLinkRequest(BaseModel):
    link_id: str
    prompt: str

# Response Model
class AIResponse(BaseModel):
    success: bool
    processing_results: str = None
    error: str = None
    service: str = None
    model: str = None
    user_id: str = None
    content_type: str = None
    original_prompt: str = None

@ai_router.get("/")
def get_ai():
    """Get AI service information"""
    return {"message": "AI Services API - Simple file/link processing"}

@ai_router.post("/process-file", response_model=AIResponse)
async def process_file(
    request: ProcessFileRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Process a file by ID"""
    logger.info(f"Processing file request")
    logger.info(f"File ID: {request.file_id}")
    logger.info(f"Prompt: {request.prompt}")
    logger.info(f"User ID: {current_user.id}")
    
    try:
        result = await ai_helper.process_file(
            file_id=request.file_id,
            prompt=request.prompt,
            user=current_user
        )
        logger.info(f"AI helper result: {result}")
        return AIResponse(**result)
    except Exception as e:
        logger.error(f"Error in process_file endpoint: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@ai_router.post("/process-link", response_model=AIResponse)
async def process_link(
    request: ProcessLinkRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Process a link by ID"""
    result = await ai_helper.process_link(
        link_id=request.link_id,
        prompt=request.prompt,
        user=current_user
    )
    return AIResponse(**result) 