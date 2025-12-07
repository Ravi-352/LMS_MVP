from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app import crud, schemas

router = APIRouter()

@router.post("/enroll", response_model=schemas.EnrollmentOut)
def enroll(e: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    # user must sign up separately; here we trust user_id provided for MVP
    en = crud.enroll_user(db, e.user_id, e.course_id)
    return en

@router.post("/progress")
def update_progress(user_id: int, course_id: int, progress: float, db: Session = Depends(get_db)):
    # progress is 0-100 float
    en = crud.update_progress(db, user_id, course_id, progress)
    if not en:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return {"status": "ok", "progress": en.progress_percent}
