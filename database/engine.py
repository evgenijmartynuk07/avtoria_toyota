from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base


SQLALCHEMY_DATABASE_URL = "sqlite:///.test.db"


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)


create_db_and_tables()


def get_db():
    return SessionLocal()
