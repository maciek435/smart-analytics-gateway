

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from app.auth.security import verify_token
from app.db import get_db
from app.models.users import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    user_id = verify_token(token)
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not user.active:
        raise HTTPException(status_code=403, detail="Access denied")

    return user

async def require_admin(user:  User = Depends(get_current_user)):
    role = user.role
    if role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return user
