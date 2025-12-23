from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app import crud, schemas, models
from app.core.auth import get_current_user, verify_csrf

router = APIRouter()

# APIRouter → Used to group related API endpoints (like /courses)
# Depends → Injects dependencies (DB session)
# HTTPException → Send proper error status to client
# Session → Type hint for database session
# get_db → Provides DB session (from earlier)
# crud → Functions that talk to the DB (Create/Read/Update/Delete)
# schemas → Pydantic models for request & response validation

#@router.post("/", response_model=schemas.CourseDetailOut)
#def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user),):
#    if not user.is_educator:
#        raise HTTPException(status_code=403, detail="Only educators can create courses")
#    
#    return crud.create_course(db, course)

@router.get("/", response_model=list[schemas.CourseOut])
def list_courses(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.list_courses(db, skip=skip, limit=limit)

# A slug is a clean, readable, URL-friendly identifier for a resource — like a course name — used in the webpage address.

@router.get("/{slug}", response_model=schemas.CourseOut)
def get_course(slug: str, db: Session = Depends(get_db)):
    c = crud.get_course_by_slug(db, slug)
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    return c

# adding course progress endpoint and  Allow preview-only for first lesson before enrollment
@router.post('/{course_id}/lessons/{lesson_id}/complete')
def mark_lesson_complete(course_id: int, lesson_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user = current_user
    user_id = user.id
    lesson = db.query(models.Lesson).get(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail='Lesson not found')
    section = db.query(models.Section).get(lesson.section_id)
    if not section or section.course_id != course_id:
        raise HTTPException(status_code=400, detail='Lesson does not belong to course')
    
    # check if user is enrolled
    enrollment = db.query(models.Enrollment).filter_by(user_id=user_id, course_id=course_id).first()

    # Check if it's the first lesson in the course
    is_preview_lesson = (
        lesson.order_index == 0 and
        lesson.section.order_index == 0  # first section, first lesson
    )

    if not enrollment and not is_preview_lesson:
        raise HTTPException(status_code=403, detail='User must be enrolled to acsess and complete lessons')
    crud.mark_lesson_completed(db, user_id, lesson_id)
    progress = crud.calculate_and_update_progress(db, user_id, course_id)
    return {'message': 'Lesson marked complete', 'progress': progress}
