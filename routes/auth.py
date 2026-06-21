from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User
from schemas import UserCreate, UserLogin

from auth.hash import hash_password, verify_password
from auth.jwt import create_access_token
from auth.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(user : UserCreate , db : AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = hash_password(user.password)

    new_user = User(
        username = user.username,
        email = user.email,
        hashed_password = hashed_pwd
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User registered successfully"}


@router.post("/login")
async def Login(user : UserLogin , db : AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": existing_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }

# Situation :(Why /me is called)                             Why /me is called
    # App loads / page refresh                   Frontend needs to know who is logged in
    # Show username in navbar                    dashboard.html calls /me to display your name
    # Verify token is still valid                If /me returns 401, token expired → redirect to login


# this is the dependancy injection 
# db : AsyncSession = Depends(get_db):

    # FastAPI:

    # Calls get_db()
    # Gets the session
    # Passes it to your function
    # Closes it after the request finishes means once you get the session you can use it in your function and you don't have to worry about closing it because FastAPI will do that for you later when the request is done.

    # So Depends is mainly about automatic lifecycle management and code reuse, not because manual creation is impossible.