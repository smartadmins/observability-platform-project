from datetime import datetime
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)

class TaskRead(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    model_config = {"from_attributes": True}
