from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from models.user_model import User

class RunBase(SQLModel):
    type: str
    input_data: str
    provider: str = "Cloud"
    output_data: Optional[str] = None

class Run(RunBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    owner_id: int = Field(foreign_key="user.id")
    
    owner: "User" = Relationship(back_populates="runs")

class RunRead(RunBase):
    id: int
    created_at: datetime
    owner_id: int