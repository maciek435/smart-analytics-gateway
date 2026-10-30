import bcrypt
import base64
import hashlib

def _prepare(password: str) -> bytes:
    return base64.b64encode(hashlib.sha256(password.encode()).digest())

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(_prepare(password),bcrypt.gensalt())
    return hashed.decode()
    
def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(_prepare(password), password_hash.encode())