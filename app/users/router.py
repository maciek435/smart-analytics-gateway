from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Source
from app.db import get_db
from app.schemas.user import UserCreate, UserResponse
from app.auth.deps import require_admin
from app.auth.security import hash_password

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("", response_model=UserResponse, dependencies=[Depends(require_admin)], status_code=201)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(select(User).where(User.email == user.email))
    result = result.scalar_one_or_none()
    
    if result is not None:
        raise HTTPException(status_code=409, detail="Email already exists")

    if user.source_id is not None:
        if user.role == "admin":
            raise HTTPException(status_code=400, detail="Admin cannot have a source_id")

        result = await db.execute(select(Source).where(Source.id == user.source_id))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(status_code=404, detail="Source not found")

    if user.role =="client" and user.source_id is None:
        raise HTTPException(status_code=400, detail="Client must have a source_id")
    

    
    
    new_user = User (
        email = user.email,
        password_hash = hash_password(user.password),
        source_id = user.source_id,
        role = user.role
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user