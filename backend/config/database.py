from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import Settings, get_settings
from sqlmodel import SQLModel, Session

settings = get_settings()

engine = create_engine(settings.DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

