from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User
from auth.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# OAuth2PasswordBearer
# from fastapi.security import OAuth2PasswordBearer

    # This is one of the most misunderstood pieces.
    # It does NOT verify JWTs.
    # It only extracts the token from:
    # Authorization: Bearer eyJhbGci...
    # Example request:
    # GET /users/me
    # Authorization: Bearer abc123
    # Then:
    # oauth2_scheme = OAuth2PasswordBearer(
    #     tokenUrl="/auth/login"
    # )
    # creates a dependency.
    # Later:
    # token: str = Depends(oauth2_scheme)
    # means:
    # token = "abc123"
    # FastAPI automatically pulls it from the Authorization header.

#     In simple words:
# Login endpoint creates token → client sends token in Authorization header → OAuth2PasswordBearer extracts it from the header → get_current_user verifies it.


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    email = payload.get("sub")

    result = await db.execute(
        select(User).where(User.email == email)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user



# Depends:
    # Depends() tells FastAPI:
    # "Before running this function, execute another function and inject its result."