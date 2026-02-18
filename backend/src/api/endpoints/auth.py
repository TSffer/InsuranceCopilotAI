from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from ...core.database import get_db
from ...domain.schemas import UserCreate, UserResponse, Token
from ...services.auth_service import AuthService
from ...core.security import create_access_token
from ...core.config import settings
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

router = APIRouter()

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register", response_model=UserResponse)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.register_user(user_create)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    # OAuth2PasswordRequestForm expects 'username' field, but we treat it as email
    return await auth_service.authenticate_user(form_data.username, form_data.password)

@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_req: RefreshRequest):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_req.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise credentials_exception
            
        access_token = create_access_token(subject=username)
        # We can optionally rotate refresh token here too, but for now just return new access token
        # Returning the SAME refresh token to keep it simple, or generate a new one if we want rotation.
        # Let's just return the new access token and echo back the refresh token (or a new one).
        # To match the Token schema, we need both.
        
        return Token(
            access_token=access_token, 
            refresh_token=refresh_req.refresh_token, 
            token_type="bearer"
        )
        
    except InvalidTokenError:
        raise credentials_exception
