from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

# User Schema
class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Pydantic V2 compatibility
    email: EmailStr
    password: str
    full_name: Optional[str] = None


# Candidate Schema
class CandidateCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    email: EmailStr
    phone: Optional[str] = None
    position_applied : str


class CandidateResponse(BaseModel):
    id: int  # Include ID for response
    name: str
    email: EmailStr
    phone: Optional[str] = None
    position_applied: str

    model_config = ConfigDict(from_attributes=True)  # Allows compatibility with SQLAlchemy models
