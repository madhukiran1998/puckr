from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from typing import Optional, List
import uuid
from datetime import datetime
import os

from ..models import (
    FileUpload, FileResponse, FileListResponse, FileType,
    UserResponse
)
from ..db.supabase_client import supabase
from .auth_router import get_current_user

router = APIRouter(prefix="/files", tags=["files"])

# Allowed file extensions and their corresponding FileType enum
ALLOWED_EXTENSIONS = {
    '.pdf': FileType.PDF,
    '.doc': FileType.WORD,
    '.docx': FileType.WORD,
}

def get_file_type(filename: str) -> FileType:
    """Determine file type based on file extension"""
    _, ext = os.path.splitext(filename.lower())
    return ALLOWED_EXTENSIONS.get(ext)

@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    is_public: bool = Form(False),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload a file to Supabase storage"""
    
    # Validate file type
    file_type = get_file_type(file.filename)
    if not file_type:
        raise HTTPException(status_code=400, detail="Only PDF and Word files are allowed")
    
    # Validate file size (50MB limit)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")
    
    # Read file content
    file_content = await file.read()
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    storage_filename = f"{file_id}{file_extension}"
    
    # Upload to Supabase storage
    try:
        storage_path = f"user-files/{current_user.id}/{storage_filename}"
        result = supabase.storage.from_("files").upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": file.content_type}
        )
        
        # Get public URL
        file_url = supabase.storage.from_("files").get_public_url(storage_path)
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
        
        # Store file metadata in database
        file_data = {
            "id": file_id,
            "user_id": str(current_user.id),
            "name": name,
            "description": description,
            "tags": tag_list,
            "is_public": is_public,
            "file_type": file_type.value,
            "file_path": storage_path,
            "file_url": file_url,
            "file_size": len(file_content),
            "mime_type": file.content_type,
            "original_filename": file.filename,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("files").insert(file_data).execute()
        
        if result.data:
            return FileResponse(**result.data[0])
        else:
            raise HTTPException(status_code=500, detail="Failed to save file metadata")
            
    except Exception as e:
        # Clean up uploaded file if database insert fails
        try:
            supabase.storage.from_("files").remove([storage_path])
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.get("/", response_model=FileListResponse)
async def list_files(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    file_type: Optional[FileType] = Query(None),
    search: Optional[str] = Query(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """List user's files with pagination and filtering"""
    
    # Build query
    query = supabase.table("files").select("*").eq("user_id", str(current_user.id))
    
    # Add filters
    if file_type:
        query = query.eq("file_type", file_type.value)
    
    if search:
        query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")
    
    # Get total count
    count_query = query
    count_result = count_query.execute()
    total = len(count_result.data)
    
    # Add pagination
    offset = (page - 1) * per_page
    query = query.range(offset, offset + per_page - 1).order("created_at", desc=True)
    
    result = query.execute()
    
    files = [FileResponse(**file) for file in result.data]
    
    return FileListResponse(
        files=files,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get file details by ID"""
    
    result = supabase.table("files").select("*").eq("id", file_id).eq("user_id", str(current_user.id)).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(**result.data[0])

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a file"""
    
    # Get file details first
    result = supabase.table("files").select("*").eq("id", file_id).eq("user_id", str(current_user.id)).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_data = result.data[0]
    
    try:
        # Delete from storage
        supabase.storage.from_("files").remove([file_data["file_path"]])
        
        # Delete from database
        supabase.table("files").delete().eq("id", file_id).execute()
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.put("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    is_public: Optional[bool] = Form(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update file metadata"""
    
    # Check if file exists and belongs to user
    result = supabase.table("files").select("*").eq("id", file_id).eq("user_id", str(current_user.id)).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Prepare update data
    update_data = {"updated_at": datetime.utcnow().isoformat()}
    
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if tags is not None:
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
        update_data["tags"] = tag_list
    if is_public is not None:
        update_data["is_public"] = is_public
    
    # Update file
    result = supabase.table("files").update(update_data).eq("id", file_id).execute()
    
    if result.data:
        return FileResponse(**result.data[0])
    else:
        raise HTTPException(status_code=500, detail="Failed to update file") 