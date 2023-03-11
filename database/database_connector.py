from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from os import environ

load_dotenv()
engine = create_engine(environ.get("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_models() -> None:
    # noinspection PyUnresolvedReferences
    import database.models
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("create")


if __name__ == '__main__':
    init_models()
