from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.db import get_db
from app.schemas.auth import TokenResponse
from app.auth.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/v1/auth")

@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    email = form_data.username
    password = form_data.password

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Nieprawidłowe dane")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Nieprawidłowe dane")

    if not user.active:
        raise HTTPException(status_code=403, detail="Zabroniono dostępu")


    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}




