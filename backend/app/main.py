from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.users_router import user_router
from .api.embeddings_router import embedding_router
from .api.search_router import search_router
from .api.ai_router import ai_router
from .api.auth_router import router as auth_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Puckr API! See /docs for all endpoints."}

app.include_router(user_router, prefix="/users", tags=["User Service"])
app.include_router(embedding_router, prefix="/embeddings", tags=["Embedding Service"])
app.include_router(search_router, prefix="/search", tags=["Search Service"])
app.include_router(ai_router, prefix="/ai", tags=["AI Service"])
app.include_router(auth_router, prefix="/api", tags=["Auth"]) 