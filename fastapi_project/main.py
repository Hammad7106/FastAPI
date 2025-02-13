from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi_project.serializers import *
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi_project.database import get_db
from fastapi_project.models import Candidate, User
from fastapi_project.auth import hash_password, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_project.auth import verify_password
from fastapi_project.background_tasks import log_candidate_creation
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk import capture_exception, capture_message
import csv
import io
from fastapi.responses import StreamingResponse

app = FastAPI(title='My First FastAPI Project')

#Sentry Exception Handler
@app.exception_handler(HTTPException)
async def sentry_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code in [401, 422]:  # Capture only unauthorized access
        capture_exception(exc)  # Send to Sentry
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


# Basic Health Check FUnction
@app.get('/')
async def health_check():
    return {"status":"I am Healthy"}


# Create a User
@app.post('/users')
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        hashed_password = hash_password(user.password)
        db_user = User(email=user.email, password=hashed_password, full_name=user.full_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": "User created successfully"}

    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Get access token on successfull login
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        capture_message(f"Failed login attempt for user: {form_data.username}", level="warning")
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# Create Candidate
@app.post("/candidates", dependencies=[Depends(get_current_user)])
def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db)):
    try:
        db_candidate = Candidate(**candidate.dict())
        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)

        # Log candidate creation asynchronously
        log_candidate_creation.delay(db_candidate.email)

        return db_candidate

    except Exception as e:
        capture_exception(e)  # Send the exception to Sentry
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# Get Candidate By ID
@app.post("/candidate/{id}", dependencies=[Depends(get_current_user)])
def get_candidate(id: int, db: Session = Depends(get_db)):
    try:
        candidate = db.query(Candidate).filter(Candidate.id == id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate Not Found")
        return candidate

    except Exception as e:
        capture_exception(e)  # Send the exception to Sentry
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# Update Candidate By ID
@app.put("/candidates/{id}", dependencies=[Depends(get_current_user)])
def update_candidate(id: int, updated_candidate: CandidateCreate, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    for key, value in updated_candidate.dict().items():
        setattr(candidate, key, value)

    db.commit()
    db.refresh(candidate)
    return candidate


# Delete Candidate by ID
@app.delete("/candidates/{id}", dependencies=[Depends(get_current_user)])
def delete_candidate(id: int, db: Session = Depends(get_db)):
    try:
        candidate = db.query(Candidate).filter(Candidate.id == id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        db.delete(candidate)
        db.commit()
        return {"message": "Candidate deleted successfully"}

    except HTTPException as http_exc:
        sentry_sdk.capture_exception(http_exc)
        raise http_exc  # Re-raise for FastAPI to handle properly

    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# Get all the Candidates through search keywords
@app.get("/all-candidates", response_model=dict)
def get_all_candidates(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search keyword"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    """ Retrieve all candidates with search and pagination. """
    try:
        query = db.query(Candidate)

        #  Search across all fields
        if search:
            query = query.filter(
                Candidate.name.ilike(f"%{search}%") |
                Candidate.email.ilike(f"%{search}%") |
                Candidate.phone.ilike(f"%{search}%") |
                Candidate.position_applied.ilike(f"%{search}%")
            )

        #  Pagination
        total_count = query.count()
        candidates = query.offset((page - 1) * limit).limit(limit).all()

        # Convert SQLAlchemy Models to Pydantic Response Models
        candidate_list = [CandidateResponse.model_validate(candidate) for candidate in candidates]

        return {
            "status": "success",
            "total_candidates": total_count,
            "page": page,
            "limit": limit,
            "candidates": candidate_list
        }

    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# Generate a CSV Report of all the candidates
@app.get("/generate-report", response_class=StreamingResponse)
def generate_report(db: Session = Depends(get_db)):
    """
    Generate a CSV report containing all candidate information.
    Optimized for large datasets by streaming the response.
    """
    try:
        candidates = db.query(Candidate).all()

        # Create a stream for CSV writing
        def generate():
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(["ID", "Name", "Email", "Phone", "Position Applied"])

            for candidate in candidates:
                writer.writerow([candidate.id, candidate.name, candidate.email,
                                 candidate.phone, candidate.position_applied])
                output.seek(0)
                yield output.read()
                output.truncate(0)  # Clear buffer after yielding

        return StreamingResponse(generate(), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=candidates_report.csv"})

    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        raise HTTPException(status_code=500, detail="Failed to generate report")
