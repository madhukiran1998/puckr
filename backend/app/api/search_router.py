from fastapi import APIRouter

search_router = APIRouter()

@search_router.get("/")
def get_search():
    return {"message": "SearchService GET endpoint"} 