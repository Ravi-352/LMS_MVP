# backend/app/routes/public.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app import crud, schemas
from typing import List

router = APIRouter()

@router.get("/courses", response_model=List[schemas.CourseDetailOut])
def list_courses(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.list_courses(db, skip=skip, limit=limit)

@router.get("/courses/{slug}", response_model=schemas.CourseDetailOut)
def get_course(slug: str, db: Session = Depends(get_db)):
    c = crud.get_course_by_slug(db, slug)
    if not c:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Course not found")
    return c

# Preview endpoint: get first section/lesson (for preview)
@router.get("/courses/{slug}/preview")
def preview_course(slug: str, db: Session = Depends(get_db)):
    course = crud.get_course_by_slug(db, slug)
    if not course:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Course not found")
    # fetch first lesson (first section ordered, lesson order)
    first_lesson = crud.get_first_lesson_for_course(db, course.id)
    return {"course": course, "preview": first_lesson}


@router.get("/courses/{course_id}/feedback")
def get_public_course_feedback(course_id: int,
                               db: Session = Depends(get_db)):
    return {
        "summary": crud.get_feedback_summary(db, course_id),
        "reviews": crud.list_feedback_for_course(db, course_id)
    }
