import asyncio
from getpass import getpass

from fastapi import Depends
from sqlalchemy import select

from app.auth.security import hash_password
from app.db import AsyncSessionLocal, get_db
from app.models.users import User
from app.schemas.user import UserCreate

async def create_admin(email:str, password:str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()

        if existing:
            print("User już zarejestrowany!")
            return

        new_user = User(
            email = email,
            password_hash = hash_password(password),
            role = "admin",
            source_id = None,
            active = True
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)




if __name__ == "__main__":
    email = input("E-mail: ")
    password = getpass("Hasło: ")
    asyncio.run(create_admin(email, password))
