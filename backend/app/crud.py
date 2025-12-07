from sqlalchemy.orm import Session, joinedload
from app import models, schemas
from sqlalchemy import func
from passlib.context import CryptContext
from datetime import datetime
from fastapi import HTTPException, status
from datetime import timezone
from app.core import security

# creates a password hashing helper using the bcrypt algorithm
# deprecated="auto" ensures compatibility with future versions, If I ever change hashing algorithms later, automatically treat the older ones as deprecated.
# But Passlib will detect the old hash and re-hash the password with the new algorithm on next login
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, user: schemas.UserCreate):

    hashed = security.hash_password(user.password)
    db_user = models.User(email=user.email, full_name=user.full_name, hashed_password=hashed, is_educator=user.is_educator, is_google_account=False, created_at=datetime.now(timezone.utc))
    db.add(db_user); db.commit(); db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()



def create_course(db: Session, course_in: schemas.CourseCreate):
    course = models.Course(title=course_in.title, slug=course_in.slug, description=course_in.description,
                           is_udemy=course_in.is_udemy, udemy_url=course_in.udemy_url)
    db.add(course); db.commit(); db.refresh(course)
    # # Only create sections and lessons for non-udemy courses
    if not course.is_udemy:

        for s_idx, s in enumerate(course_in.sections or []):
            sec = models.Section(course_id=course.id, title=s.title, order=s_idx)
            db.add(sec); db.commit(); db.refresh(sec)
            for l_idx, l in enumerate(s.lessons or []):
                lesson = models.Lesson(section_id=sec.id, title=l.title, type=l.type,
                                    youtube_url=l.youtube_url, pdf_url=l.pdf_url, order=l_idx)
                db.add(lesson)
            db.commit()
    return course

def list_courses(db: Session, skip=0, limit=50):
    return db.query(models.Course).offset(skip).limit(limit).all()

# ---------- helper lookups ----------
def get_course_by_id(db: Session, course_id: int):
    return db.query(models.Course).options(
        joinedload(models.Course.sections).joinedload(models.Section.lessons).joinedload(models.Lesson.assessments).joinedload(models.Assessment.choices)
    ).filter(models.Course.id == course_id).first()


#def get_course_by_id(db, course_id: int):
#    return db.query(models.Course).get(course_id)

def get_course_by_slug(db: Session, slug: str):
    return db.query(models.Course).filter(models.Course.slug == slug).first()

def get_lesson(db: Session, lesson_id: int):
    return db.query(models.Lesson).get(lesson_id)

def lesson_belongs_to_course(db: Session, lesson_id: int, course_id: int) -> bool:
    # a lesson -> section -> course relationship check
    lesson = get_lesson(db, lesson_id)
    if not lesson:
        return False
    return lesson.section.course_id == course_id

def is_user_enrolled(db: Session, user_id: int, course_id: int) -> bool:
    e = db.query(models.Enrollment).filter_by(user_id=user_id, course_id=course_id).first()
    return e is not None

def is_preview_lesson(db: Session, lesson_id: int) -> bool:
    # find if lesson is first lesson of first section in its course
    lesson = get_lesson(db, lesson_id)
    if not lesson:
        return False
    # assuming Section.order and Lesson.order exist
    first_section = db.query(models.Section).filter_by(course_id=lesson.section.course_id).order_by(models.Section.order).first()
    if not first_section:
        return False
    first_lesson = db.query(models.Lesson).filter_by(section_id=first_section.id).order_by(models.Lesson.order).first()
    return first_lesson and first_lesson.id == lesson_id

def enroll_user(db: Session, user_id: int, course_id: int):
    e = db.query(models.Enrollment).filter(models.Enrollment.user_id==user_id, models.Enrollment.course_id==course_id).first()
    if e:
        return e
    e = models.Enrollment(user_id=user_id, course_id=course_id, progress_percent=0.0)
    db.add(e); db.commit(); db.refresh(e)
    return e

def update_progress(db: Session, user_id: int, course_id: int, progress: float):
    e = db.query(models.Enrollment).filter(models.Enrollment.user_id==user_id, models.Enrollment.course_id==course_id).first()
    if not e:
        return None
    e.progress_percent = progress
    if progress >= 100:
        e.status = "completed"
    db.commit(); db.refresh(e)
    return e

def create_course_with_educator(db: Session, course_in: schemas.CourseCreate, educator_id: int):
    # create the course and set educator_id
    course = models.Course(title=course_in.title, slug=course_in.slug, description=course_in.description, is_udemy=course_in.is_udemy, udemy_url=course_in.udemy_url, educator_id=educator_id)
    db.add(course)
    db.commit()
    db.refresh(course)
    # create sections/lessons if present
    for s_idx, s in enumerate(course_in.sections or []):
        sec = models.Section(course_id=course.id, title=s.title, order=s_idx)
        db.add(sec)
        db.commit()
        db.refresh(sec)
        for l_idx, l in enumerate(s.lessons or []):
            lesson = models.Lesson(section_id=sec.id, title=l.title, type=l.type,
                                   youtube_url=l.youtube_url, pdf_url=l.pdf_url, order=l_idx)
            db.add(lesson)
        db.commit()
    return course




def list_enrollments_for_course(db: Session, course_id: int):
    rows = (
        db.query(
            models.Enrollment.user_id,
            models.User.email,
            models.Enrollment.progress_percent,
            models.Enrollment.status
        )
        .join(models.User, models.User.id == models.Enrollment.user_id)
        .filter(models.Enrollment.course_id == course_id)
        .all()
    )

    return [
        {
            "user_id": r.user_id,
            "email": r.email,
            "progress_percent": r.progress_percent,
            "status": r.status,
        }
        for r in rows
    ]



# --- Assessments / Choices ---
def create_assessment(db: Session, a: schemas.AssessmentCreate):
    ass = models.Assessment(lesson_id=a.lesson_id, question_markdown=a.question_markdown,
                            image_url=a.image_url, max_score=a.max_score, explanation=a.explanation)
    db.add(ass); db.commit(); db.refresh(ass)
    return ass

def add_choice(db: Session, assessment_id: int, text: str, is_correct: bool=False, explanation: str=None):
    ch = models.Choice(assessment_id=assessment_id, text=text, is_correct=is_correct, explanation=explanation)
    db.add(ch); db.commit(); db.refresh(ch)
    return ch

def get_assessments_for_lesson(db: Session, lesson_id: int):
    return db.query(models.Assessment).filter(models.Assessment.lesson_id==lesson_id).all()


#def add_choice(db: Session, c: schemas.ChoiceCreate):
#    ch = models.Choice(assessment_id=c.assessment_id, text=c.text, is_correct=c.is_correct)
#    db.add(ch); db.commit(); db.refresh(ch)
#    return ch

# --- Attempts & student answers ---
def create_assessment_attempt(db: Session, user_id: int, assessment_id: int):
    # find last attempt number
    last = db.query(func.max(models.AssessmentAttempt.attempt_number)).filter_by(user_id=user_id, assessment_id=assessment_id).scalar()
    next_attempt = (last or 0) + 1
    attempt = models.AssessmentAttempt(user_id=user_id, assessment_id=assessment_id, attempt_number=next_attempt)
    db.add(attempt); db.commit(); db.refresh(attempt)
    return attempt

def record_student_answer_on_attempt(db: Session, attempt_id: int, choice_id: int):
    choice = db.query(models.Choice).get(choice_id)
    is_correct = bool(choice.is_correct) if choice else False
    score = 1.0 if is_correct else 0.0
    sa = models.StudentAnswer(attempt_id=attempt_id, choice_id=choice_id, is_correct=is_correct, score=score)
    db.add(sa); db.commit(); db.refresh(sa)
    return sa

def finalize_assessment_attempt(db: Session, attempt_id: int):
    # sum scores
    total = db.query(func.sum(models.StudentAnswer.score)).filter(models.StudentAnswer.attempt_id==attempt_id).scalar() or 0.0
    attempt = db.query(models.AssessmentAttempt).get(attempt_id)
    attempt.score = float(total)
    db.commit(); db.refresh(attempt)
    return attempt

# def record_student_answer(db: Session, user_id: int, assessment_id: int, choice_id: int):
#    sa = models.StudentAnswer(user_id=user_id, assessment_id=assessment_id, choice_id=choice_id)
#    db.add(sa); db.commit(); db.refresh(sa)
#    return sa



# --- Progress helpers  ---
def course_total_lessons(db: Session, course_id: int) -> int:
    return db.query(func.count(models.Lesson.id)).join(models.Section).filter(models.Section.course_id==course_id).scalar() or 0

def completed_lessons_for_user(db: Session, user_id: int, course_id: int) -> int:
    
    # Count completed lessons by this user that belong to lessons of this course
    
    # completed_lessons = db.query(func.count(models.StudentLesson.lesson_id)).filter(
    #    models.StudentLesson.user_id == user_id,
    #    models.StudentLesson.lesson_id.in_(
    #        db.query(models.Lesson.id).join(models.Section).filter(models.Section.course_id == course_id)
    #    )
    #).scalar() or 0
    
    completed_lessons = db.query(func.count(models.StudentLesson.lesson_id)).join(models.Lesson, models.StudentLesson.lesson_id==models.Lesson.id).join(models.Section).filter(
        models.StudentLesson.user_id==user_id,
        models.Section.course_id==course_id
    ).scalar() or 0

    return completed_lessons

def calculate_and_update_progress(db: Session, user_id: int, course_id: int):
    total_lessons = course_total_lessons(db, course_id)
    completed = completed_lessons_for_user(db, user_id, course_id)
    progress = round((completed / total_lessons) * 100, 2) if total_lessons > 0 else 0.0
    enrollment = db.query(models.Enrollment).filter_by(user_id=user_id, course_id=course_id).first()
    if not enrollment:
        # in production we enforce enrollment; here ensure update only if exists
        raise HTTPException(status_code=403, detail="Must enroll before accessing lessons")
        return progress
    else:
        enrollment.progress_percent = progress
        if progress >= 100:
            enrollment.status = "completed"

    db.commit(); db.refresh(enrollment)
    return progress

def course_progress_percent(db: Session, user_id: int, course_id: int):
    e = db.query(models.Enrollment).filter(models.Enrollment.user_id==user_id, models.Enrollment.course_id==course_id).first()
    return e.progress_percent if e else 0.0

def mark_lesson_completed(db, user_id: int, lesson_id: int):
    """
    Insert StudentLesson if not exists. Return the StudentLesson instance.
    """
    existing = db.query(models.StudentLesson).filter_by(user_id=user_id, lesson_id=lesson_id).first()
    if existing:
        return existing
    sl = models.StudentLesson(user_id=user_id, lesson_id=lesson_id)
    db.add(sl)
    db.commit()
    db.refresh(sl)
    return sl


# ---------- Upsert helpers (create or update) ----------
def _upsert_choice(db: Session, assessment: models.Assessment, choice_in: dict):
    # choice_in has optional id; create or update
    if choice_in.get("id"):
        ch = db.query(models.Choice).get(choice_in["id"])
        if not ch:
            # fallback create
            ch = models.Choice(assessment_id=assessment.id, text=choice_in["text"], is_correct=choice_in.get("is_correct", False), explanation=choice_in.get("explanation"))
            db.add(ch)
        else:
            ch.text = choice_in["text"]
            ch.is_correct = choice_in.get("is_correct", False)
            ch.explanation = choice_in.get("explanation")
    else:
        ch = models.Choice(assessment_id=assessment.id, text=choice_in["text"], is_correct=choice_in.get("is_correct", False), explanation=choice_in.get("explanation"))
        db.add(ch)
    db.flush()
    return ch

def _upsert_assessment(db: Session, lesson: models.Lesson, ass_in: dict):
    if ass_in.get("id"):
        ass = db.query(models.Assessment).get(ass_in["id"])
        if not ass:
            ass = models.Assessment(lesson_id=lesson.id,
                                    question_markdown=ass_in["question_markdown"],
                                    image_url=ass_in.get("image_url"),
                                    max_score=ass_in.get("max_score", 1),
                                    explanation=ass_in.get("explanation"))
            db.add(ass)
            db.flush()
        else:
            ass.question_markdown = ass_in["question_markdown"]
            ass.image_url = ass_in.get("image_url")
            ass.max_score = ass_in.get("max_score", 1)
            ass.explanation = ass_in.get("explanation")
    else:
        ass = models.Assessment(lesson_id=lesson.id,
                                question_markdown=ass_in["question_markdown"],
                                image_url=ass_in.get("image_url"),
                                max_score=ass_in.get("max_score", 1),
                                explanation=ass_in.get("explanation"))
        db.add(ass)
        db.flush()

    # Sync choices: incoming choices are the desired final set. We'll upsert by id and delete any choices not present.
    incoming_choice_ids = []
    for ch_in in ass_in.get("choices", []):
        ch = _upsert_choice(db, ass, ch_in)
        incoming_choice_ids.append(ch.id)

    # delete choices not in incoming set
    existing_choice_ids = [c.id for c in ass.choices]
    for rid in existing_choice_ids:
        if rid not in incoming_choice_ids:
            db.query(models.Choice).filter_by(id=rid).delete()

    db.flush()
    return ass

def _upsert_lesson(db: Session, section: models.Section, lesson_in: dict):
    if lesson_in.get("id"):
        lesson = db.query(models.Lesson).get(lesson_in["id"])
        if not lesson:
            lesson = models.Lesson(section_id=section.id,
                                   title=lesson_in["title"],
                                   type=lesson_in["type"],
                                   youtube_url=lesson_in.get("youtube_url"),
                                   pdf_url=lesson_in.get("pdf_url"),
                                   order=lesson_in.get("order", 0))
            db.add(lesson)
            db.flush()
        else:
            lesson.title = lesson_in["title"]
            lesson.type = lesson_in["type"]
            lesson.youtube_url = lesson_in.get("youtube_url")
            lesson.pdf_url = lesson_in.get("pdf_url")
            lesson.order = lesson_in.get("order", lesson.order if hasattr(lesson, "order") else 0)
    else:
        lesson = models.Lesson(section_id=section.id,
                               title=lesson_in["title"],
                               type=lesson_in["type"],
                               youtube_url=lesson_in.get("youtube_url"),
                               pdf_url=lesson_in.get("pdf_url"),
                               order=lesson_in.get("order", 0))
        db.add(lesson)
        db.flush()

    # Sync assessments
    incoming_assessment_ids = []
    for ass_in in lesson_in.get("assessments", []):
        ass = _upsert_assessment(db, lesson, ass_in)
        incoming_assessment_ids.append(ass.id)

    # delete assessments not in incoming set
    existing_ass_ids = [a.id for a in lesson.assessments]
    for rid in existing_ass_ids:
        if rid not in incoming_assessment_ids:
            # delete related student attempts/answers first (safe cleanup)
            db.query(models.StudentAnswer).filter(models.StudentAnswer.choice_id.in_(
                db.query(models.Choice.id).filter(models.Choice.assessment_id == rid)
            )).delete(synchronize_session=False)
            db.query(models.AssessmentAttempt).filter_by(assessment_id=rid).delete()
            db.query(models.Choice).filter_by(assessment_id=rid).delete()
            db.query(models.Assessment).filter_by(id=rid).delete()

    db.flush()
    return lesson

def _upsert_section(db: Session, course: models.Course, section_in: dict):
    if section_in.get("id"):
        sec = db.query(models.Section).get(section_in["id"])
        if not sec:
            sec = models.Section(course_id=course.id, title=section_in["title"], order=section_in.get("order", 0))
            db.add(sec)
            db.flush()
        else:
            sec.title = section_in["title"]
            sec.order = section_in.get("order", sec.order if hasattr(sec, "order") else 0)
    else:
        sec = models.Section(course_id=course.id, title=section_in["title"], order=section_in.get("order", 0))
        db.add(sec)
        db.flush()

    incoming_lesson_ids = []
    for lesson_in in section_in.get("lessons", []):
        l = _upsert_lesson(db, sec, lesson_in)
        incoming_lesson_ids.append(l.id)

    # delete lessons not in incoming set (and cascade delete assessments/attempts)
    existing_lesson_ids = [l.id for l in sec.lessons]
    for rid in existing_lesson_ids:
        if rid not in incoming_lesson_ids:
            # delete student lesson completions
            db.query(models.StudentLesson).filter_by(lesson_id=rid).delete()
            # delete assessments under lesson (handled in _upsert_lesson when removing assessments)
            db.query(models.Lesson).filter_by(id=rid).delete()

    db.flush()
    return sec


# ---------- Top-level course updater ----------
def update_course_full(db: Session, course_id: int, course_in: dict, educator_id: int):
    """
    course_in: dict representation (matching CourseCreate/CourseUpdate schema)
    This function synchronizes DB to reflect course_in. Atomic.
    """
    course = db.query(models.Course).get(course_id)
    if not course:
        return None

    # ensure educator owns the course
    if course.educator_id != educator_id:
        raise PermissionError("Not allowed. You are not the educator of this course.")

    # Begin transaction for atomicity
    with db.begin():
        # Update course meta
        course.title = course_in.get("title", course.title)
        course.slug = course_in.get("slug", course.slug)
        course.description = course_in.get("description", course.description)
        course.is_udemy = course_in.get("is_udemy", course.is_udemy)
        course.udemy_url = course_in.get("udemy_url", course.udemy_url)

        # Sync sections
        incoming_section_ids = []
        for sec_in in course_in.get("sections", []):
            sec = _upsert_section(db, course, sec_in)
            incoming_section_ids.append(sec.id)

        # delete sections not in incoming set
        existing_section_ids = [s.id for s in course.sections]
        for rid in existing_section_ids:
            if rid not in incoming_section_ids:
                # delete lessons & assessments recursively
                # delete student progress for lessons in this section
                lesson_ids = [l.id for l in db.query(models.Lesson).filter_by(section_id=rid).all()]
                for lid in lesson_ids:
                    db.query(models.StudentLesson).filter_by(lesson_id=lid).delete()
                    # delete attempts and choices and assessments
                    ass_ids = [a.id for a in db.query(models.Assessment).filter_by(lesson_id=lid).all()]
                    for aid in ass_ids:
                        db.query(models.StudentAnswer).filter_by(attempt_id=aid).delete()
                    db.query(models.AssessmentAttempt).filter(models.AssessmentAttempt.assessment_id.in_(ass_ids)).delete()
                    db.query(models.Choice).filter(models.Choice.assessment_id.in_(ass_ids)).delete()
                    db.query(models.Assessment).filter_by(lesson_id=lid).delete()
                db.query(models.Lesson).filter_by(section_id=rid).delete()
                db.query(models.Section).filter_by(id=rid).delete()

        db.flush()

    # Refresh and return full course detail
    db.refresh(course)
    return get_course_by_id(db, course_id)  # returns joined load nested object


# Feedback

def can_give_feedback(db: Session, user_id: int, course_id: int) -> bool:
    enrollment = db.query(models.Enrollment).filter_by(
        user_id=user_id, course_id=course_id
    ).first()
    return bool(enrollment and enrollment.progress_percent >= 25)

def upsert_feedback(db: Session, user_id: int, course_id: int, fb: schemas.FeedbackCreate):
    feedback = db.query(models.CourseFeedback).filter_by(
        user_id=user_id, course_id=course_id
    ).first()

    if feedback:
        feedback.rating = fb.rating
        feedback.comment = fb.comment_markdown
    else:
        feedback = models.Feedback(
            user_id=user_id,
            course_id=course_id,
            rating=fb.rating,
            comment=fb.comment_markdown
        )
        db.add(feedback)

    db.commit()
    db.refresh(feedback)
    return feedback

def list_feedback_for_course(db: Session, course_id: int, limit: int = 50):
    return db.query(models.CourseFeedback).filter_by(course_id=course_id).order_by(
        models.CourseFeedback.created_at.desc()
    ).limit(limit).all()

def get_feedback_summary(db: Session, course_id: int):
    from sqlalchemy import func
    avg_rating = db.query(func.avg(models.CourseFeedback.rating)).filter_by(course_id=course_id).scalar()
    count = db.query(models.CourseFeedback.id).filter_by(course_id=course_id).count()
    return {
        "avg_rating": round(avg_rating or 0, 2),
        "total_reviews": count
    }

#def add_feedback(db: Session, f: schemas.FeedbackCreate):
#    fb = models.CourseFeedback(user_id=f.user_id, course_id=f.course_id, rating=f.rating, comment_markdown=f.comment_markdown)
#    db.add(fb); db.commit(); db.refresh(fb)
#    return fb