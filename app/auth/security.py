from datetime import datetime, timedelta, timezone

import bcrypt
import base64
import hashlib

import jwt

from app.config import settings


def _prepare(password: str) -> bytes:
    return base64.b64encode(hashlib.sha256(password.encode()).digest())

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(_prepare(password),bcrypt.gensalt())
    return hashed.decode()
    
def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(_prepare(password), password_hash.encode())

def create_access_token(user_id: int) -> str:
    now = datetime.now(tz=timezone.utc)
    
    payload = {
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "iat": now,
        "sub": str(user_id),
    }
    return jwt.encode(payload, key=settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
