# backend/app/routes/students.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.sessions import get_db
from app.core.auth import require_role, get_current_user, verify_csrf
from app import crud, schemas, models
from app.core.logging_config import logger
from typing import List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Enroll
@router.post("/enroll", response_model=schemas.EnrollmentOut)
#def enroll(course_id: int, current_user: models.User = Depends(require_role("student")), db: Session = Depends(get_db), _csrf=Depends(verify_csrf)):
def enroll(enr: schemas.EnrollmentCreate, current_user: models.User = Depends(require_role("student")), db: Session = Depends(get_db), _csrf=Depends(verify_csrf)):
    # ignore e.user_id from client; use current_user
    course_id = enr.course_id
    payment = None
    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 🔮 payment-ready gate (inactive for now)
    if course.price_cents > 0:
        payment = crud.get_successful_payment(
            db,
            user_id=current_user.id,
            course_id=course_id
        )
        if not payment:
            raise HTTPException(status_code=402, detail="Payment required")
    
    try:
        
        enrollment = crud.enroll_user(db, current_user.id, course_id)
        logger.info(f"User {current_user.id} enrolled in course {course_id}")    
        return enrollment
    
    except IntegrityError:
        logger.warning(f"Duplicate enrollment for user {current_user.id} in course {course_id}")
        raise HTTPException(status_code=409, detail="You are already enrolled in this course.")

    except HTTPException as e:
        # Log expected business errors
        logger.info(f"Enrollment HTTP error: {e.detail}")
        raise e

    except Exception as e:
        # Unexpected error => Debugging required
        logger.error(f"Unknown error enrolling user {current_user.id} in course {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected server error")
    
@router.get("/courses", response_model=list[schemas.StudentCourseOut])
def my_courses(
    current_user: models.User = Depends(require_role("student")),
    db: Session = Depends(get_db)
):
    rows = (
        db.query(models.Course, models.Enrollment.progress_percent)
        .join(models.Enrollment, models.Enrollment.course_id == models.Course.id)
        .filter(models.Enrollment.user_id == current_user.id)
        .all()
    )

    return [
        {
            "course_id": c.id,
            "course_title": c.title,
            "course_slug": c.slug,
            "course_description": c.description,
            "progress_percent": p,
        }
        for c, p in rows
    ]


# Get course detail (with lessons and assessments, hiding correct answers)
@router.get("/courses/{course_id}", response_model=schemas.CourseDetailOut)
def student_get_course_detail(course_id: int, current_user: models.User = Depends(require_role("student")), db: Session = Depends(get_db)):
    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    # For student view, hide correct answers in assessments
    # Implement a helper to assemble full nested CourseDetail with choices but without is_correct flag.
    return crud.get_course_detail_for_student(db, course_id, current_user.id)


# List assessments for a course (only if enrolled except for preview logic)
@router.get("/courses/{course_id}/assessments", response_model=List[schemas.AssessmentQuestionOut])
def list_assessments_for_course(course_id: int, current_user: models.User = Depends(require_role("student")), db: Session = Depends(get_db)):
    # optionally require enrollment except preview logic
    if not crud.is_user_enrolled(db, current_user.id, course_id):
        # allow only if preview lesson or other rule
        raise HTTPException(status_code=403, detail="Enroll to access assessments")
    return crud.get_assessments_for_course(db, course_id)

# Mark lesson complete (only enrolled except for preview logic inside crud or route)
@router.post("/courses/{course_id}/lessons/{lesson_id}/complete")
def mark_complete(course_id: int, lesson_id: int, current_user: models.User = Depends(require_role("student")), db: Session = Depends(get_db), _csrf=Depends(verify_csrf)):
    # Check preview allowance (crud helper will ensure preview logic if you choose)
    course = crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    lesson = crud.get_lesson(db, lesson_id)
    if not lesson or not crud.lesson_belongs_to_course(db, lesson_id, course_id):
        raise HTTPException(status_code=400, detail="Invalid lesson")

    # preview logic: allow first lesson even if not enrolled
    if not crud.is_user_enrolled(db, current_user.id, course_id):
        if not crud.is_preview_lesson(db, lesson_id):
            raise HTTPException(status_code=403, detail="Enroll to access full course")

    crud.mark_lesson_completed(db, current_user.id, lesson_id)
    progress = crud.calculate_and_update_progress(db, current_user.id, course_id)
    return {"message":"Lesson marked complete", "progress": progress}

@router.get("/courses/{course_id}/progress")
def get_progress(course_id: int, current_user: models.User = Depends(require_role("student")), db: Session = Depends(get_db)):
    enrolled = crud.is_user_enrolled(db, current_user.id, course_id)
    if not enrolled:
        return {"is_enrolled": False, "progress_percent": 0}
    return {"is_enrolled": True, "progress_percent": crud.course_progress_percent(db, current_user.id, course_id)}


@router.post("/assessments/{assessment_id}/submit", response_model=schemas.AttemptResultOut)
def submit_assessment(assessment_id: int, payload: dict, current_user: models.User = Depends(require_role("student")), db: Session = Depends(get_db), _csrf=Depends(verify_csrf)):
    """
    payload example:
    {
      "answers": [
        {"choice_id": 12},
        {"choice_id": 15}
      ]
    }
    """
    
    # in future when we want to free audit option for courses but need payment for assessments, we can check enrollment + payment status here; commented for now.
    #assessment = crud.get_assessment(db, assessment_id)
    #if not assessment:
    #    raise HTTPException(status_code=404, detail="Assessment not found")
    #course_id = crud.get_course_id_for_assessment(db, assessment_id)

    #if not crud.is_user_enrolled(db, current_user.id, course_id):
    #    raise HTTPException(403, "Enroll to attempt assessment")

    answers = payload.get("answers", [])
    # create attempt
    attempt = crud.create_assessment_attempt(db, current_user.id, assessment_id)
    q_results = []
    for a in answers:
        ch_id = a.get("choice_id")
        sa = crud.record_student_answer_on_attempt(db, attempt.id, ch_id)
        q_results.append({
            "question_id": sa.attempt_id, # we'll populate properly below
        })
    attempt = crud.finalize_assessment_attempt(db, attempt.id)
    # assemble question-level results: query answers, choices, correct ids etc.
    question_results = []
    answers_objs = db.query(models.StudentAnswer).filter_by(attempt_id=attempt.id).all()
    for ans in answers_objs:
        choice = db.query(models.Choice).get(ans.choice_id) if ans.choice_id else None
        assessment = db.query(models.Assessment).get(choice.assessment_id) if choice else None
        # find correct choice id for that assessment
        correct_choice = db.query(models.Choice).filter_by(assessment_id=assessment.id, is_correct=True).first() if assessment else None
        question_results.append({
            "question_id": assessment.id if assessment else None,
            "selected_choice_id": choice.id if choice else None,
            "is_correct": ans.is_correct,
            "correct_choice_id": correct_choice.id if correct_choice else None,
            "score": ans.score,
            "explanation": assessment.explanation if assessment and ans.is_correct else None
        })
    return {
        "attempt_id": attempt.id,
        "assessment_id": assessment_id,
        "attempt_number": attempt.attempt_number,
        "total_score": attempt.score,
        "question_results": question_results
    }

# Get feedbacks for a course
@router.post("/courses/{course_id}/feedback", response_model=schemas.FeedbackOut)
def give_feedback(course_id: int,
                  fb: schemas.FeedbackCreate,
                  current_user: models.User = Depends(require_role("student")),
                  db: Session = Depends(get_db), _csrf=Depends(verify_csrf)):

    if not crud.can_give_feedback(db, current_user.id, course_id):
        raise HTTPException(status_code=403, detail="Complete at least 25% to review")

    return crud.upsert_feedback(db, current_user.id, course_id, fb)
