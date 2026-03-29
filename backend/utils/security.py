from typing import Annotated
import jwt
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta, timezone
from models.user_model import User, UserCreate, TokenData

from sqlalchemy.orm import Session
from config.database import get_session
from config.settings import Settings, get_settings


password_hash = PasswordHash.recommended()

DUMMY_HASH = "ffa35hukfjds5930gfhvsdfnfah0qc(=//+3+rgfskflklrw'sfal"

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    settings = get_settings() 
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    session: Annotated[Session, Depends(get_session)]
):
    settings = get_settings() # Ayarları dahil et
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # settings üzerinden doğru şekilde okuyoruz
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub") # Artık email değil, username okuyoruz
        
        if username is None:
            raise credentials_exception
            
    except InvalidTokenError:
        raise credentials_exception

    # Veritabanında username ile eşleşen kullanıcıyı buluyoruz
    user = session.query(User).filter(User.username == username).first()
    
    if user is None:
        raise credentials_exception
        
    return user

async def register_user(session: Annotated[Session, Depends(get_session)], user: UserCreate):
    db_user = session.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.hashed_password)
    new_user = User(
        username=user.username,
        email=user.email,
        disabled=user.disabled if user.disabled else False,
        hashed_password=hashed_password
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

def authenticate_user(session: Annotated[Session, Depends(get_session)], username: str, password: str):
    user = session.query(User).filter(User.username == username).first()
    if not user:
        # Zamanlama saldırılarını önlemek için sahte bir hash doğrulaması yapıyoruz   
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

