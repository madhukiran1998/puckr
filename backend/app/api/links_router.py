from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
import uuid
from datetime import datetime
from urllib.parse import urlparse

from ..models import (
    LinkCreate, LinkResponse, LinkListResponse, LinkType,
    UserResponse
)
from ..db.supabase_client import supabase
from .auth_router import get_current_user

router = APIRouter(prefix="/links", tags=["links"])

def detect_link_type(url: str) -> LinkType:
    """Automatically detect link type based on URL"""
    parsed_url = urlparse(url.lower())
    domain = parsed_url.netloc
    
    if "twitter.com" in domain or "x.com" in domain:
        return LinkType.TWITTER
    elif "youtube.com" in domain or "youtu.be" in domain:
        return LinkType.YOUTUBE
    elif "github.com" in domain:
        return LinkType.GITHUB
    elif "reddit.com" in domain:
        return LinkType.REDDIT
    elif any(blog_domain in domain for blog_domain in ["medium.com", "dev.to", "hashnode.dev", "substack.com", "blogspot.com", "wordpress.com"]):
        return LinkType.BLOG
    else:
        return LinkType.OTHER

@router.post("/", response_model=LinkResponse)
async def create_link(
    link_data: LinkCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new link"""
    
    # Auto-detect link type if not provided
    if not link_data.link_type:
        link_data.link_type = detect_link_type(str(link_data.url))
    
    # Prepare link data
    link_id = str(uuid.uuid4())
    link_db_data = {
        "id": link_id,
        "user_id": str(current_user.id),
        "title": link_data.title,
        "description": link_data.description,
        "tags": link_data.tags or [],
        "is_public": link_data.is_public,
        "url": str(link_data.url),
        "link_type": link_data.link_type.value,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    try:
        result = supabase.table("links").insert(link_db_data).execute()
        
        if result.data:
            return LinkResponse(**result.data[0])
        else:
            raise HTTPException(status_code=500, detail="Failed to create link")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create link: {str(e)}")

@router.get("/", response_model=LinkListResponse)
async def list_links(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    link_type: Optional[LinkType] = Query(None),
    search: Optional[str] = Query(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """List user's links with pagination and filtering"""
    
    # Build query
    query = supabase.table("links").select("*").eq("user_id", str(current_user.id))
    
    # Add filters
    if link_type:
        query = query.eq("link_type", link_type.value)
    
    if search:
        query = query.or_(f"title.ilike.%{search}%,description.ilike.%{search}%,url.ilike.%{search}%")
    
    # Get total count
    count_query = query
    count_result = count_query.execute()
    total = len(count_result.data)
    
    # Add pagination
    offset = (page - 1) * per_page
    query = query.range(offset, offset + per_page - 1).order("created_at", desc=True)
    
    result = query.execute()
    
    links = [LinkResponse(**link) for link in result.data]
    
    return LinkListResponse(
        links=links,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/{link_id}", response_model=LinkResponse)
async def get_link(
    link_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get link details by ID"""
    
    result = supabase.table("links").select("*").eq("id", link_id).eq("user_id", str(current_user.id)).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Link not found")
    
    return LinkResponse(**result.data[0])

@router.put("/{link_id}", response_model=LinkResponse)
async def update_link(
    link_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    is_public: Optional[bool] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update link metadata"""
    
    # Check if link exists and belongs to user
    result = supabase.table("links").select("*").eq("id", link_id).eq("user_id", str(current_user.id)).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Prepare update data
    update_data = {"updated_at": datetime.utcnow().isoformat()}
    
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if tags is not None:
        update_data["tags"] = tags
    if is_public is not None:
        update_data["is_public"] = is_public
    
    # Update link
    result = supabase.table("links").update(update_data).eq("id", link_id).execute()
    
    if result.data:
        return LinkResponse(**result.data[0])
    else:
        raise HTTPException(status_code=500, detail="Failed to update link")

@router.delete("/{link_id}")
async def delete_link(
    link_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a link"""
    
    # Check if link exists and belongs to user
    result = supabase.table("links").select("*").eq("id", link_id).eq("user_id", str(current_user.id)).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Link not found")
    
    try:
        # Delete from database
        supabase.table("links").delete().eq("id", link_id).execute()
        
        return {"message": "Link deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete link: {str(e)}") 