from fastapi import FastAPI
from .api.users_router import user_router
from .api.embeddings_router import embedding_router
from .api.search_router import search_router
from .api.ai_router import ai_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Puckr API! See /docs for all endpoints."}

app.include_router(user_router, prefix="/users", tags=["User Service"])
app.include_router(embedding_router, prefix="/embeddings", tags=["Embedding Service"])
app.include_router(search_router, prefix="/search", tags=["Search Service"])
app.include_router(ai_router, prefix="/ai", tags=["AI Service"]) 