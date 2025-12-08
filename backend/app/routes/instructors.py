# backend/app/routes/instructors.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app.core.auth import require_role, verify_csrf
from app import crud, schemas, models

router = APIRouter()

#@router.post("/courses", response_model=schemas.CourseOut)
#def create_course(course: schemas.CourseCreate, current_user: models.User = Depends(require_role("instructor")), db: Session = Depends(get_db)):
#    # set educator id to current user
#    course_obj = crud.create_course_with_educator(db, course, educator_id=current_user.id)
#    return course_obj

#@router.put("/courses/{course_id}")
#def update_course(course_id: int, course: schemas.CourseCreate, current_user: models.User = Depends(require_role("instructor")), db: Session = Depends(get_db)):
#    existing = crud.get_course_by_id(db, course_id)
#    if not existing or existing.educator_id != current_user.id:
#        raise HTTPException(status_code=403, detail="Not allowed")
#    return crud.update_course(db, course_id, course)


@router.post("/courses", response_model=schemas.CourseDetailOut)
def create_course(course_in: schemas.CourseCreate, current_user: models.User = Depends(require_role("instructor")), db: Session = Depends(get_db), _csrf=Depends(verify_csrf)):
    course = crud.create_course_with_educator(db, course_in, educator_id=current_user.id)
    return crud.get_course_by_id(db, course.id)


@router.get("/courses", response_model=list[schemas.CourseDetailOut])
def list_my_courses(current_user: models.User = Depends(require_role("instructor")),
                    db: Session = Depends(get_db)):
    courses = db.query(models.Course).filter_by(educator_id=current_user.id).all()
    return courses


@router.put("/courses/{course_id}", response_model=schemas.CourseDetailOut)
def update_course(course_id: int, course_in: schemas.CourseUpdate, current_user: models.User = Depends(require_role("instructor")), db: Session = Depends(get_db), _csrf=Depends(verify_csrf)):
    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course.educator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed. You are not the educator of this course.")
    try:
        updated = crud.update_course_full(db, course_id, course_in.dict(), educator_id=current_user.id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if not updated:
        raise HTTPException(status_code=404, detail="Course not found after update")
    # return nested detail (APEX)
    return crud.get_course_by_id(db, course_id)

@router.get("/courses/{course_id}", response_model=schemas.CourseDetailOut)
def get_course_detail(course_id: int,
                      current_user: models.User = Depends(require_role("instructor")),
                      db: Session = Depends(get_db)):
    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    if course.educator_id != current_user.id:
        raise HTTPException(403, "Not allowed")
    return course

@router.get("/courses/{course_id}/lessons", response_model=list[schemas.LessonOut])
def list_course_lessons(course_id: int,
                        current_user: models.User = Depends(require_role("instructor")),
                        db: Session = Depends(get_db)):
    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.educator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    lessons = crud.list_lessons_for_course(db, course_id)
    return lessons

@router.post("/courses/{course_id}/lessons", response_model=schemas.LessonOut, status_code=status.HTTP_201_CREATED)
def create_course_lesson(course_id: int, payload: schemas.LessonCreate,
                         current_user: models.User = Depends(require_role("instructor")),
                         db: Session = Depends(get_db),
                         _csrf=Depends(verify_csrf)):
    """
    payload example:
    {
      "title": "Intro",
      "type": "video",   # video|pdf|article
      "youtube_url": "...",
      "pdf_url": "...",
      "order": 0,
      "assessments": [ ... optional assessments dicts ... ]
    }
    """
    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.educator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    lesson = crud.create_lesson_simple(db, course_id, payload)
    return lesson

@router.delete("/lessons/{lesson_id}", response_model=dict)
def delete_lesson(lesson_id: int,
                  current_user: models.User = Depends(require_role("instructor")),
                  db: Session = Depends(get_db),
                  _csrf=Depends(verify_csrf)):
    # Ensure the instructor owns the course for this lesson
    lesson = db.query(models.Lesson).filter_by(id=lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    # verify instructor owns the parent course
    section = db.query(models.Section).filter_by(id=lesson.section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Parent section not found")
    course = db.query(models.Course).filter_by(id=section.course_id).first()
    if not course or course.educator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    # perform safe delete using crud helper
    crud.delete_lesson_simple(db, lesson_id)
    return {"ok": True}

# add endpoints to upload content, add assessments etc. for instructor
@router.post("/courses/{course_id}/assessments", response_model=dict)
def instructor_create_assessment(course_id: int, payload: dict, current_user: models.User = Depends(require_role("instructor")), db: Session = Depends(get_db), _csrf=Depends(verify_csrf)):
    """
    payload example:
    {
      "lesson_id": 12,
      "question_markdown": "...",
      "image_url": null,
      "max_score": 1,
      "explanation": "explain",
      "choices": [
        {"text":"A", "is_correct": false, "explanation": "..."},
        {"text":"B", "is_correct": true, "explanation": "..."}
      ]
    }
    """
    # validate course ownership
    course = crud.get_course_by_id(db, course_id)
    if course.educator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed. You are not the educator of this course.")
    a_in = schemas.AssessmentCreate(
        lesson_id=payload.get("lesson_id"),
        question_markdown=payload.get("question_markdown"),
        image_url=payload.get("image_url"),
        max_score=payload.get("max_score", 1),
        explanation=payload.get("explanation")
    )
    ass = crud.create_assessment(db, a_in)
    for ch in payload.get("choices", []):
        crud.add_choice(db, ass.id, ch["text"], ch.get("is_correct", False), ch.get("explanation"))
    return {"id": ass.id}

# Also add instructor endpoints:
# GET /courses/{course_id}/students that returns list of enrolled students + progress:

# call crud.list_enrollments_for_course(db, course_id) that returns user_id, user.email, progress_percent, status

#@router.get("/courses/{course_id}/students", response_model=list[dict])
@router.get("/courses/{course_id}/students")
def get_enrolled_students(course_id: int,
                          current_user: models.User = Depends(require_role("instructor")),
                          db: Session = Depends(get_db)):
    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.educator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return crud.list_enrollments_for_course(db, course_id)



#@router.get("/courses/{course_id}/students")
#def list_students(course_id: int, current_user: models.User = Depends(require_role("instructor")), db: Session = Depends(get_db)):
#    course = crud.get_course_by_id(db, course_id)
#    if not course:
#        raise HTTPException(status_code=404, detail="Course not found")
#    if course.educator_id != current_user.id:
#        raise HTTPException(status_code=403, detail="Not allowed")
#    return crud.list_enrollments_for_course(db, course_id)

# if required also create - 
# #GET /courses/{course_id}/students/{user_id}/progress returns detailed progress + lesson completion list (for review/grading)

# checking own courses

@router.get("/courses/{course_id}/feedback")
def instructor_view_feedback(course_id: int,
                             current_user: models.User = Depends(require_role("instructor")),
                             db: Session = Depends(get_db)):

    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    if course.educator_id != current_user.id:
        raise HTTPException(403, "Not allowed")

    return {
        "summary": crud.get_feedback_summary(db, course_id),
        "reviews": crud.list_feedback_for_course(db, course_id)
    }
