from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app.core.auth import require_role, get_current_user
from app import crud, schemas, models

router = APIRouter()

@router.post("/", response_model=dict)
def post_feedback(f: schemas.FeedbackCreate, current_user: models.User = Depends(require_role("student")), db: Session = Depends(get_db)):
    # Ensure user has at least 25% progress before allowing feedback
    progress = crud.course_progress_percent(db, f.user_id, f.course_id)
    if progress < 25.0:
        raise HTTPException(status_code=403, detail="Feedback allowed after 25\%\ course progress")
    fb = crud.add_feedback(db, f)
    return {"id": fb.id}

@router.get("/course/{course_id}", response_model=list)
def get_feedbacks(course_id: int, db: Session = Depends(get_db)):
    items = db.query(__import__("app").models.CourseFeedback).filter_by(course_id=course_id).all()
    return items
