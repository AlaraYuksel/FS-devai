from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from config.settings import Settings, get_settings
from config.database import create_db_and_tables, get_session

from models.user_model import User, UserCreate, UserRead, UserUpdate, Token, TokenData, UserBase
from models.run_model import Run, RunBase, RunRead

app = FastAPI()

SessionDependency = Annotated[Session, Depends(get_session)]

# CORS Ayarları
origins = [
    "http://localhost",
    "http://localhost:5432", 
    "http://localhost:5173", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Server is running!"}

@app.get("/info")
async def get_info(settings: Annotated[Settings, Depends(get_settings)]):
    return {
        "database": settings.DATABASE_URL,
        "api_key_status": "Loaded" if settings.GEMINI_API_KEY else "Missing"
    }

@app.post("/create-user", response_model=UserCreate)
async def create_user(session: SessionDependency, user: UserCreate):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user