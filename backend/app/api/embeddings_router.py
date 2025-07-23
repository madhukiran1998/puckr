from fastapi import APIRouter

embedding_router = APIRouter()

@embedding_router.get("/")
def get_embeddings():
    return {"message": "EmbeddingService GET endpoint"} 