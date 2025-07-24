from fastapi import APIRouter, HTTPException, Depends
from app.db.supabase_client import supabase
from app.models import UserResponse
from app.api.auth_router import verify_jwt_token

user_router = APIRouter()

@user_router.get("/me", response_model=UserResponse)
def get_current_user_profile(user_id: str = Depends(verify_jwt_token)):
    """Get current user profile (alternative to /api/auth/me)"""
    response = supabase.table("users").select("*").eq("id", user_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**response.data)

@user_router.get("/")
def list_users():
    """List all users (for admin purposes - add auth later)"""
    response = supabase.table("users").select("id, username, email, avatar_url, created_at").execute()
    return {"users": response.data} 