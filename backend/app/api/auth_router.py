from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import os
from urllib.parse import urlencode
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.db.supabase_client import supabase
from app.models import UserOAuth, UserResponse

router = APIRouter()
security = HTTPBearer()

# GitHub OAuth Configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_OAUTH_AUTHORIZE_URL = os.getenv("GITHUB_OAUTH_AUTHORIZE_URL", "https://github.com/login/oauth/authorize")
GITHUB_OAUTH_TOKEN_URL = os.getenv("GITHUB_OAUTH_TOKEN_URL", "https://github.com/login/oauth/access_token")
GITHUB_USER_API_URL = os.getenv("GITHUB_USER_API_URL", "https://api.github.com/user")

# Redirect URIs
REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/api/auth/github/callback")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "168"))  # Default: 1 week

# Frontend URLs
FRONTEND_HOME_URL = os.getenv("FRONTEND_HOME_URL", "http://localhost:3000/")
FRONTEND_LOGIN_URL = os.getenv("FRONTEND_LOGIN_URL", "http://localhost:3000/login")

def create_jwt_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode = {"exp": expire, "sub": user_id}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/auth/github/login")
def github_login():
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "read:user user:email",
    }
    url = f"{GITHUB_OAUTH_AUTHORIZE_URL}?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/auth/github/callback")
async def github_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code in callback.")
    
    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_resp = await client.post(
            GITHUB_OAUTH_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token.")
        
        # Fetch user info
        user_resp = await client.get(
            GITHUB_USER_API_URL,
            headers={"Authorization": f"token {access_token}"}
        )
        user_data = user_resp.json()

    # Upsert user into Supabase users table
    github_id = str(user_data.get("id"))
    email = user_data.get("email")
    username = user_data.get("login")
    avatar_url = user_data.get("avatar_url")
    
    # Create user data using the proper model
    user_oauth = UserOAuth(
        provider="github",
        provider_user_id=github_id,
        email=email,
        username=username,
        avatar_url=avatar_url
    )
    
    upsert_data = user_oauth.model_dump(exclude_none=True)
    
    # Upsert by provider + provider_user_id
    response = supabase.table("users").upsert(upsert_data, on_conflict="provider, provider_user_id").execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to upsert user in Supabase.")

    # Get the user's id from the upserted data
    user_id = None
    if response.data and isinstance(response.data, list) and len(response.data) > 0:
        user_id = response.data[0].get("id")
    if not user_id:
        raise HTTPException(status_code=500, detail="Could not determine user id after upsert.")

    # Generate JWT token
    jwt_token = create_jwt_token(str(user_id))
    
    # Redirect to frontend with token in URL (frontend will grab it and store in localStorage)
    redirect_url = f"{FRONTEND_HOME_URL}?token={jwt_token}"
    return RedirectResponse(url=redirect_url, status_code=302)

@router.get("/auth/me", response_model=UserResponse)
def get_current_user(user_id: str = Depends(verify_jwt_token)):
    # Fetch user from Supabase by id
    response = supabase.table("users").select("*").eq("id", user_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=401, detail="User not found")
    return UserResponse(**response.data)

@router.get("/auth/logout")
def logout():
    # For JWT, logout is handled client-side by removing the token
    return RedirectResponse(url=FRONTEND_LOGIN_URL, status_code=302) 