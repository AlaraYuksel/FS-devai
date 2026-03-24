from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import Settings, get_settings
from config.database import create_db_and_tables, get_session

app = FastAPI()

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

@app.get("/")
async def root():
    return {"message": "Server is running!"}

@app.get("/info")
async def get_info(settings: Annotated[Settings, Depends(get_settings)]):
    return {
        "database": settings.DATABASE_URL,
        "api_key_status": "Loaded" if settings.GEMINI_API_KEY else "Missing"
    }