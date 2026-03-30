from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.run_model import Run

class UserBase(SQLModel):
    username: str
    email: str = Field(index=True, unique=True)
    disabled: bool = False

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

    runs: list["Run"] = Relationship(back_populates="owner") 

class UserCreate(UserBase):
    hashed_password: str

class UserRead(SQLModel):
    id: int
    username: str
    email: str

class UserUpdate(SQLModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    disabled: bool | None = None

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: str | None = None