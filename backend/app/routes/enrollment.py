from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.sessions import get_db
from app import crud, schemas, models
from app.core.auth import get_current_user, verify_csrf

router = APIRouter()

#@router.post("/enrollment", response_model=schemas.EnrollmentOut)
@router.post("/{course_id}", response_model=schemas.EnrollmentOut)
#def enroll(course_id: int, e: schemas.EnrollmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
def enroll(course_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user), _csrf=Depends(verify_csrf)):
    # Only allow enrolling for self by a student
    if current_user.is_educator:
        raise HTTPException(status_code=403, detail="Instructors cannot enroll in courses")
    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 🔮 future payment hook
    if course.price_cents > 0:
        raise HTTPException(
            status_code=402,
            detail="Payment required",
        )
    
    en = crud.enroll_user(db, user_id=current_user.id, course_id=course_id)
    return en

@router.post("/{course_id}/progress")
def update_progress(user_id: int, course_id: int, progress: float, db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    
    if current_user.is_educator:
        raise HTTPException(status_code=403, detail="Instructors do not have course progress")

    enrollment = crud.get_enrollment(
        db,
        user_id=current_user.id,
        course_id=course_id,
    )

    if not enrollment:
        raise HTTPException(status_code=404, detail="Not enrolled in this course")

    # progress is 0-100 float
    if progress < 0 or progress > 100:
        raise HTTPException(status_code=400, detail="Progress must be between 0 and 100")

    updated = crud.update_progress(
        db,
        user_id=current_user.id,
        course_id=course_id,
        progress=progress,
    )

    
    return {"status": "ok", "progress": updated.progress_percent}
