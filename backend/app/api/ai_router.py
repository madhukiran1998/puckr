from fastapi import APIRouter

ai_router = APIRouter()

@ai_router.get("/")
def get_ai():
    return {"message": "AiServices GET endpoint"} 