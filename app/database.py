from typing import Annotated
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, DeclarativeBase
from fastapi import Depends

from app.config import settings

# database engine
DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(DATABASE_URL, echo=True)


# session dependency for path operations
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


# Base for SQLAchemy tables declaration
class Base(DeclarativeBase):
    pass

def create_db_and_tables():
    Base.metadata.create_all(engine)