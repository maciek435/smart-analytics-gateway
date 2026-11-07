from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    schema_version: str | None = None


class SourceResponse(BaseModel):
    id: int
    name: str
    schema_version: str | None
    active: bool

    model_config = {"from_attributes": True}