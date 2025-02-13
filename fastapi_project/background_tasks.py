from sqlalchemy.orm import Session
from fastapi_project.database import SessionLocal
from fastapi_project.models import CandidateLog
from celery import Celery

celery = Celery(
    "tasks",
    broker="sqla+sqlite:///celerydb.sqlite",  # Use SQLite instead of Redis/RabbitMQ
    backend="db+sqlite:///celery_results.sqlite"  # Store task results in SQLite
)


@celery.task
def log_candidate_creation(email: str):
    """Celery task to log candidate creation in the database."""
    db: Session = SessionLocal()

    try:
        log_entry = CandidateLog(candidate_email=email)
        db.add(log_entry)
        db.commit()
        return f"Logged candidate creation for {email}"

    except Exception as e:
        db.rollback()
        return f"Failed to log candidate: {str(e)}"

    finally:
        db.close()

