from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from ..domain.models import User
from ..domain.schemas import UserCreate, Token
from ..core.security import get_password_hash, verify_password, create_access_token

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_create: UserCreate) -> User:
        # Check if email already exists
        result = await self.db.execute(select(User).where(User.email == user_create.email))
        if result.scalars().first():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Check if username exists (if provided)
        if user_create.username:
            result = await self.db.execute(select(User).where(User.username == user_create.username))
            if result.scalars().first():
                raise HTTPException(
                    status_code=400,
                    detail="Username already taken"
                )

        new_user = User(
            email=user_create.email,
            username=user_create.username,
            password_hash=get_password_hash(user_create.password),
            role=user_create.role
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def authenticate_user(self, email: str, password: str) -> Token:
        print(f"DEBUG: Authenticating user {email}")
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        print(f"DEBUG: User found: {user}")
        
        if not user or not verify_password(password, user.password_hash):
            print("DEBUG: Authentication failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        access_token = create_access_token(subject=user.email)
        print("DEBUG: Token created successfully")
        return Token(access_token=access_token, token_type="bearer")
