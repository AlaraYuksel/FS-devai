from sqlmodel import Field, SQLModel
from .user_model import User
from typing import Optional
from sqlmodel import Relationship
from datetime import datetime

class RunCreate(SQLModel):
    type: str
    input_data: str
    provider: Optional[str] = "Cloud"

class RunBase(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type: str
    input_data: str
    output_data: str
    provider: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    owner_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="runs")

class RunRead(SQLModel):
    id: int
    type: str
    input_data: str
    output_data: str
    provider: str
    created_at: datetime
    owner_id: int
