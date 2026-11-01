from typing import Literal

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)
    role: Literal["client", "admin"]
    source_id: int | None = None

class UserResponse(BaseModel):
    id: int
    email: str
    role: Literal["client", "admin"]
    source_id: int | None = None
    active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
