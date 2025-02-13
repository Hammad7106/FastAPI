from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


# User Model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)


# candidate Model
class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    position_applied = Column(String, nullable=False)



class CandidateLog(Base):
    __tablename__ = "candidate_logs"

    id = Column(Integer, primary_key=True, index=True)
    candidate_email = Column(String, nullable=False)
    action = Column(String, default="Created")  # Action Type (e.g., Created, Updated, Deleted)
    timestamp = Column(DateTime, default=datetime.utcnow)  # Automatically stores current time
