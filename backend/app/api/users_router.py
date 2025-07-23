from fastapi import APIRouter, HTTPException
from app.db.supabase_client import supabase
from pydantic import BaseModel

class User(BaseModel):
    email: str
    password: str

user_router = APIRouter()

@user_router.post("/")
def create_user(user: User):
    response = supabase.auth.sign_up({
        "email": user.email,
        "password": user.password,
    })
    if response.user:
        return {"message": "User created successfully", "user_id": response.user.id}
    else:
        raise HTTPException(status_code=400, detail=response.error.message)


@user_router.get("/")
def get_users():
    return {"message": "UserServices GET endpoint"} 