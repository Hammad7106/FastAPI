from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

URL_DATABASE = 'postgresql://postgres:postgresql@localhost:5432/fastapi'
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
