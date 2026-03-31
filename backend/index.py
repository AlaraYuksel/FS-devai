from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from config.settings import Settings, get_settings
from config.database import create_db_and_tables, get_session

from utils.security import get_current_user, get_current_active_user, register_user, create_access_token, verify_password, get_password_hash, authenticate_user
from models.user_model import User, UserCreate, UserRead, UserUpdate, Token, TokenData, UserBase
from models.run_model import Run, RunBase, RunRead
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from datetime import datetime, timedelta
from controllers.llm_controller import generate_commit_message

app = FastAPI()

SessionDependency = Annotated[Session, Depends(get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

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


# Auth Endpoints

@app.get("/info")
async def get_info(settings: Annotated[Settings, Depends(get_settings)],token: Annotated[str, Depends(oauth2_scheme)]):
    return {
        "database": settings.DATABASE_URL,
        "api_key_status": "Loaded" if settings.GEMINI_API_KEY else "Missing"
    }

@app.post("/auth/register", response_model=UserCreate)
async def register_user_endpoint(session: SessionDependency, user: UserCreate):
    return await register_user(session, user)

@app.post("/auth/login", response_model=Token)
async def login_for_access_token(
    session: SessionDependency,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    settings = get_settings()
    user = authenticate_user(session, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, # Token içine username koyuyoruz
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/")
async def read_users_me(
    current_user: Annotated[UserRead, Depends(get_current_active_user)],
) -> UserRead:
    return current_user

# Run Endpoints

@app.get("/users/runs/")
async def read_user_runs(
    current_user: Annotated[RunRead, Depends(get_current_active_user)],
    session: SessionDependency
) -> list[RunRead]:
    user_runs = session.query(Run).filter(Run.owner_id == current_user.id).all()
    return [RunRead.from_orm(run) for run in user_runs]

@app.post("/users/runs/")
async def create_user_run(
    run: RunBase,
    current_user: Annotated[UserRead, Depends(get_current_active_user)],
    session: SessionDependency
) -> Run:
    
    new_run = Run.model_validate(run, update={"owner_id": current_user.id, "output_data": generate_commit_message(run.input_data)})

    session.add(new_run)
    session.commit()
    session.refresh(new_run)

    return new_run