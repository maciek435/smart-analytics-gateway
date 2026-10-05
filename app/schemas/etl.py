from pydantic import BaseModel
from typing import Literal

class ETLRunResponse(BaseModel):
    status: Literal["completed"]
    clean_count: int
    error_count: int