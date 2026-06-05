from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload
from app import models, schemas
from sqlalchemy import func
from passlib.context import CryptContext
from datetime import datetime
from fastapi import HTTPException, status
from datetime import timezone
from app.core import security
from slugify import slugify
import secrets, hashlib
from datetime import timedelta
import logging
import re

# Using __name__ is a production best-practice. It automatically namespaces 
# your logs to the actual file path (e.g., "app.crud.enrollment"), 
# making it incredibly easy to track down exactly where an error dropped.
logger = logging.getLogger(__name__)

# creates a password hashing helper using the bcrypt algorithm
# deprecated="auto" ensures compatibility with future versions, If I ever change hashing algorithms later, automatically treat the older ones as deprecated.
# But Passlib will detect the old hash and re-hash the password with the new algorithm on next login
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

RESET_TOKEN_EXPIRY_MINUTES = 30


def create_user(db: Session, user: schemas.UserCreate):

    hashed = security.hash_password(user.password)
    db_user = models.User(email=user.email, full_name=user.full_name, hashed_password=hashed, is_educator=user.is_educator, is_google_account=False, created_at=datetime.now(timezone.utc))
    db.add(db_user); db.commit(); db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_password_reset_token(db: Session, user_id: int):
    token_raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token_raw.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRY_MINUTES)
    prt = models.PasswordResetToken(user_id=user_id, token_hash=token_hash, is_used=False, expires_at=expires_at)
    db.add(prt); db.commit(); db.refresh(prt)
    return token_raw  # return the plain token to be sent via email

def create_course(db: Session, course_in: schemas.CourseCreate):
    course = models.Course(title=course_in.title, slug=course_in.slug, description=course_in.description,
                           is_udemy=course_in.is_udemy, udemy_url=course_in.udemy_url)
    db.add(course); 
    db.flush()  # Secure the ID without writing a permanent commit yet
    #db.commit(); db.refresh(course)
    # # Only create sections and lessons for non-udemy courses
    if not course.is_udemy:

        for s_idx, s in enumerate(course_in.sections or []):
            sec = models.Section(course_id=course.id, title=s.title, order=s_idx)
            db.add(sec); 
            db.flush()  # Secure the section ID for downstream lessons safely
            #db.commit(); db.refresh(sec)
            for l_idx, l in enumerate(s.lessons or []):
                lesson = models.Lesson(section_id=sec.id, title=l.title, type=l.type,
                                    youtube_url=l.youtube_url, pdf_url=l.pdf_url, order=l_idx)
                db.add(lesson)
                db.flush()  # Secure the lesson ID for downstream assessments safely
    db.commit()
    db.refresh(course)
    return course

def list_courses(db: Session, skip=0, limit=50):
    return db.query(models.Course).offset(skip).limit(limit).all()

def list_public_courses(db: Session, skip=0, limit=50):
    return (
        db.query(models.Course)
        .filter(models.Course.is_published == True)
        .offset(skip)
        .limit(limit)
        .all()
    )

def list_instructor_courses(db, instructor_id):
    return (
        db.query(models.Course)
        .filter(models.Course.educator_id == instructor_id)
        .all()
    )



# ---------- helper lookups ----------
def get_course_by_id_internal(db: Session, course_id: int):
    """
    Uses selectinload execution strategies to build structural entity trees.
    Avoids Cartesian network wire payload bloat caused by standard joinedload queries.
    """
    return (
        db.query(models.Course)
        .options(
            selectinload(models.Course.sections)
            .selectinload(models.Section.lessons)
            .selectinload(models.Lesson.assessments)
            .selectinload(models.Assessment.choices)
        )
        .filter(models.Course.id == course_id)
        .first()
    )

def get_published_course_by_id(db: Session, course_id: int):
    """
    Fixed Cartesian product issue by migrating execution from joinedload to selectinload.
    """
    return (
        db.query(models.Course)
        .options(
            selectinload(models.Course.sections)
            .selectinload(models.Section.lessons)
            .selectinload(models.Lesson.assessments)
            .selectinload(models.Assessment.choices)
        )
        .filter(
            models.Course.id == course_id,
            models.Course.is_published == True
        )
        .first()
    )

#def get_course_by_id(db, course_id: int):
#    return db.query(models.Course).get(course_id)

def get_published_course_by_slug(db: Session, slug: str):
    return (
        db.query(models.Course)
        .filter(
            models.Course.slug == slug,
            models.Course.is_published == True
        )
        .first()
    )

#def get_course_by_slug(db: Session, slug: str):
#    return db.query(models.Course).filter(models.Course.slug == slug).first()

def get_lesson(db: Session, lesson_id: int):
    return db.query(models.Lesson).get(lesson_id)

def lesson_belongs_to_course(db: Session, lesson_id: int, course_id: int) -> bool:
    # a lesson -> section -> course relationship check
    lesson = get_lesson(db, lesson_id)
    if not lesson:
        return False
    #return lesson.section.course_id == course_id
    result = db.query(models.Lesson).join(models.Section).filter(models.Lesson.id == lesson_id, models.Section.course_id == course_id).exists().scalar()
    return result

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
    
    try:
        e = models.Enrollment(user_id=user_id, course_id=course_id, progress_percent=0.0)
        db.add(e); db.commit(); db.refresh(e)
        return e
    except IntegrityError:
        db.rollback() #essential to rollback the failed transaction before next operations
        #gracefull fallback to returning the record that won the race
        e = db.query(models.Enrollment).filter(models.Enrollment.user_id==user_id, models.Enrollment.course_id==course_id).first()
        return e
    except Exception as unexpected_err:
        # Tier 3: Global System Failure Catch-all
        db.rollback()
        logger.critical(f"System panic during user enrollment: {str(unexpected_err)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected system error occurred."
        )
    

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
    slug = generate_unique_slug(db, course_in.title)
    # course = models.Course(title=course_in.title, slug=course_in.slug, description=course_in.description, is_udemy=course_in.is_udemy, udemy_url=course_in.udemy_url, educator_id=educator_id)
    
    #pricing rules
    if course_in.is_udemy:
        price_cents = 0
        currency = None
    else:
        price_cents = course_in.price_cents if course_in.price_cents is not None else 0
        currency = course_in.currency if course_in.currency is not None else "INR"

    course = models.Course(title=course_in.title, slug=slug, description=course_in.description, is_udemy=course_in.is_udemy, udemy_url=course_in.udemy_url, educator_id=educator_id, price_cents=price_cents, currency=currency)
    
    db.add(course)
    db.flush() # flush to get course.id for sections, but not commit yet for atomicity
    #db.commit()
    #db.refresh(course)
    
    # create default section for self-hosted courses

    if not course.is_udemy:
        sec = models.Section(course_id=course.id, title="Introduction", order=0)
        db.add(sec)
        db.commit()
        db.refresh(sec)
    else:
        db.commit()  # commit the course even for udemy since no sections/lessons to create
    
    db.refresh(course)

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

def completed_lesson_ids_for_user(db: Session, user_id: int, course_id: int) -> list[int]:
    lesson_ids = (
        db.query(models.StudentLesson.lesson_id)
        .join(models.Lesson, models.StudentLesson.lesson_id == models.Lesson.id)
        .join(models.Section, models.Lesson.section_id == models.Section.id)
        .filter(
            models.StudentLesson.user_id == user_id,
            models.Section.course_id == course_id
        )
        .all()
    )
    return [lid[0] for lid in lesson_ids]
# ---------- Upsert helpers (create or update) ----------


def generate_unique_slug(db, title):
    """
    Generates a unique URL slug using an O(1) database I/O pattern.
    Fetches all matching namespace paths in a single round-trip to compute increments in memory.
    """
    base = slugify(title)
    
    # Fetch all slugs matching the prefix pattern in a single query
    results = (
        db.query(models.Course.slug)
        .filter(models.Course.slug.like(f"{base}%"))
        .all()
    )
    existing_slugs = {r[0] for r in results}

    if base not in existing_slugs:
        return base

    # Extract maximum numerical suffix using regex pattern matching
    pattern = re.compile(rf"^{re.escape(base)}-(\d+)$")
    max_counter = 0
    
    for s in existing_slugs:
        match = pattern.match(s)
        if match:
            max_counter = max(max_counter, int(match.group(1)))

    return f"{base}-{max_counter + 1}"


def _upsert_choice(db: Session, assessment_id: int, choice_in: dict) -> models.Choice:
    ch_id = choice_in.get("id")
    if ch_id:
        ch = db.query(models.Choice).get(ch_id)
        if ch:
            ch.text = choice_in["text"]
            ch.is_correct = choice_in.get("is_correct", False)
            ch.explanation = choice_in.get("explanation")
            return ch

    ch = models.Choice(
        assessment_id=assessment_id,
        text=choice_in["text"],
        is_correct=choice_in.get("is_correct", False),
        explanation=choice_in.get("explanation")
    )
    db.add(ch)
    db.flush()
    return ch


def _upsert_assessment(db: Session, lesson_id: int, ass_in: dict, valid_choice_ids: list) -> models.Assessment:
    ass_id = ass_in.get("id")
    if ass_id:
        ass = db.query(models.Assessment).get(ass_id)
        if ass:
            ass.question_markdown = ass_in["question_markdown"]
            ass.image_url = ass_in.get("image_url")
            ass.max_score = ass_in.get("max_score", 1)
            ass.explanation = ass_in.get("explanation")
        else:
            ass = models.Assessment(
                lesson_id=lesson_id,
                question_markdown=ass_in["question_markdown"],
                image_url=ass_in.get("image_url"),
                max_score=ass_in.get("max_score", 1),
                explanation=ass_in.get("explanation")
            )
            db.add(ass)
            db.flush()
    else:
        ass = models.Assessment(
            lesson_id=lesson_id,
            question_markdown=ass_in["question_markdown"],
            image_url=ass_in.get("image_url"),
            max_score=ass_in.get("max_score", 1),
            explanation=ass_in.get("explanation")
        )
        db.add(ass)
        db.flush()

    for ch_in in ass_in.get("choices", []):
        ch = _upsert_choice(db, ass.id, ch_in)
        valid_choice_ids.append(ch.id)

    return ass


def _upsert_lesson(db: Session, section_id: int, lesson_in: dict, valid_assessment_ids: list, valid_choice_ids: list) -> models.Lesson:
    l_id = lesson_in.get("id")
    if l_id:
        lesson = db.query(models.Lesson).get(l_id)
        if lesson:
            lesson.title = lesson_in["title"]
            lesson.type = lesson_in["type"]
            lesson.youtube_url = lesson_in.get("youtube_url")
            lesson.pdf_url = lesson_in.get("pdf_url")
            lesson.order = lesson_in.get("order", lesson.order if hasattr(lesson, "order") else 0)
        else:
            lesson = models.Lesson(
                section_id=section_id, title=lesson_in["title"], type=lesson_in["type"],
                youtube_url=lesson_in.get("youtube_url"), pdf_url=lesson_in.get("pdf_url"), order=lesson_in.get("order", 0)
            )
            db.add(lesson)
            db.flush()
    else:
        lesson = models.Lesson(
            section_id=section_id, title=lesson_in["title"], type=lesson_in["type"],
            youtube_url=lesson_in.get("youtube_url"), pdf_url=lesson_in.get("pdf_url"), order=lesson_in.get("order", 0)
        )
        db.add(lesson)
        db.flush()

    for ass_in in lesson_in.get("assessments", []):
        ass = _upsert_assessment(db, lesson.id, ass_in, valid_choice_ids)
        valid_assessment_ids.append(ass.id)

    return lesson


def _upsert_section(db: Session, course_id: int, section_in: dict, valid_lesson_ids: list, valid_assessment_ids: list, valid_choice_ids: list) -> models.Section:
    sec_id = section_in.get("id")
    if sec_id:
        sec = db.query(models.Section).get(sec_id)
        if sec:
            sec.title = section_in["title"]
            sec.order = section_in.get("order", sec.order if hasattr(sec, "order") else 0)
        else:
            sec = models.Section(course_id=course_id, title=section_in["title"], order=section_in.get("order", 0))
            db.add(sec)
            db.flush()
    else:
        sec = models.Section(course_id=course_id, title=section_in["title"], order=section_in.get("order", 0))
        db.add(sec)
        db.flush()

    for lesson_in in section_in.get("lessons", []):
        l = _upsert_lesson(db, sec.id, lesson_in, valid_assessment_ids, valid_choice_ids)
        valid_lesson_ids.append(l.id)

    return sec


# ─── MAIN TRANSACTION ENTRIES & CORE BULK PURGE PIPELINE ───

def update_course_full(db: Session, course_id: int, course_in: dict, educator_id: int):
    """
    Main entry point for atomic full course configuration tree synchronization.
    """
    course = db.query(models.Course).get(course_id)
    if not course:
        return None

    if course.educator_id != educator_id:
        raise PermissionError("Not allowed. You are not the educator of this course.")

    # Tracking arrays to identify records present in the incoming payload
    valid_section_ids = []
    valid_lesson_ids = []
    valid_assessment_ids = []
    valid_choice_ids = []

    try:
        # Update course metadata root
        course.title = course_in.get("title", course.title)
        course.slug = course_in.get("slug", course.slug)
        course.description = course_in.get("description", course.description)
        course.is_udemy = course_in.get("is_udemy", course.is_udemy)
        course.udemy_url = course_in.get("udemy_url", course.udemy_url)
        db.flush()

        # Step 1: Top-down mapping and upsert parsing
        for sec_in in course_in.get("sections", []):
            sec = _upsert_section(db, course.id, sec_in, valid_lesson_ids, valid_assessment_ids, valid_choice_ids)
            valid_section_ids.append(sec.id)

        # Step 2: Discover baseline state currently committed in the DB
        all_current_sections = db.query(models.Section).filter_by(course_id=course.id).all()
        current_section_ids = [s.id for s in all_current_sections]

        if current_section_ids:
            all_current_lessons = db.query(models.Lesson).filter(models.Lesson.section_id.in_(current_section_ids)).all()
            current_lesson_ids = [l.id for l in all_current_lessons]

            if current_lesson_ids:
                all_current_assessments = db.query(models.Assessment).filter(models.Assessment.lesson_id.in_(current_lesson_ids)).all()
                current_assessment_ids = [a.id for a in all_current_assessments]

                # ─── UNIFIED BOTTOM-UP BATCH DELETION ───
                
                # A. Identify and drop omitted choices and user answers from modified assessments
                assessments_to_delete_ids = [aid for aid in current_assessment_ids if aid not in valid_assessment_ids]
                
                if assessments_to_delete_ids:
                    # Clear out downstream student dependencies safely
                    attempts = db.query(models.AssessmentAttempt).filter(models.AssessmentAttempt.assessment_id.in_(assessments_to_delete_ids)).all()
                    attempt_ids = [att.id for att in attempts]
                    
                    if attempt_ids:
                        db.query(models.StudentAnswer).filter(models.StudentAnswer.attempt_id.in_(attempt_ids)).delete(synchronize_session=False)
                        db.query(models.AssessmentAttempt).filter(models.AssessmentAttempt.id.in_(attempt_ids)).delete(synchronize_session=False)

                    db.query(models.Choice).filter(models.Choice.assessment_id.in_(assessments_to_delete_ids)).delete(synchronize_session=False)
                    db.query(models.Assessment).filter(models.Assessment.id.in_(assessments_to_delete_ids)).delete(synchronize_session=False)

                # Purge single modified choices within assessments that were kept
                if current_assessment_ids:
                    choices_to_delete_q = db.query(models.Choice).filter(models.Choice.assessment_id.in_(current_assessment_ids))
                    if valid_choice_ids:
                        choices_to_delete_q = choices_to_delete_q.filter(~models.Choice.id.in_(valid_choice_ids))
                    choices_to_delete_q.delete(synchronize_session=False)

            # B. Identify and drop omitted lessons and tracking records
            lessons_to_delete_ids = [lid for lid in current_lesson_ids if lid not in valid_lesson_ids]
            if lessons_to_delete_ids:
                db.query(models.StudentLesson).filter(models.StudentLesson.lesson_id.in_(lessons_to_delete_ids)).delete(synchronize_session=False)
                db.query(models.Lesson).filter(models.Lesson.id.in_(lessons_to_delete_ids)).delete(synchronize_session=False)

        # C. Identify and drop omitted sections
        sections_to_delete_ids = [sid for sid in current_section_ids if sid not in valid_section_ids]
        if sections_to_delete_ids:
            db.query(models.Section).filter(models.Section.id.in_(sections_to_delete_ids)).delete(synchronize_session=False)

        # Step 3: Atomic commit boundary savepoint
        db.commit()
        db.refresh(course)
        
    except Exception as e:
        db.rollback()
        logger.critical(f"Aborting full transaction sync on course ID {course_id} due to an unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to synchronize structural course changes cleanly."
        )
    return get_course_by_id_internal(db, course_id)  # returns joined load nested object

def create_default_section(db: Session, course_id: int, title: str = "Section 1"):
    """Create and return a default/first section for course if none exists."""
    sec = models.Section(course_id=course_id, title=title, order=0)
    db.add(sec)
    db.flush()
    return sec

def list_lessons_for_course(db: Session, course_id: int):
    """Return lessons belonging to a course ordered by section.order then lesson.order."""
    return (
        db.query(models.Lesson)
          .join(models.Section, models.Lesson.section_id == models.Section.id)
          .filter(models.Section.course_id == course_id)
          .order_by(models.Section.order, models.Lesson.order)
          .all()
    )

def create_lesson_simple(db: Session, course_id: int, lesson_in: dict):
    """
    Create a lesson in first section of course (create section if none exists).
    lesson_in: dict with keys { title, type, youtube_url, pdf_url, order (optional), assessments (optional) }
    Returns the created Lesson ORM object.
    """
    # find a section
    section = db.query(models.Section).filter_by(course_id=course_id).order_by(models.Section.order).first()
    if not section:
        section = create_default_section(db, course_id)

    lesson = models.Lesson(
        section_id=section.id,
        title=lesson_in.get("title"),
        type=lesson_in.get("type", "video"),
        youtube_url=lesson_in.get("youtube_url"),
        pdf_url=lesson_in.get("pdf_url"),
        order=lesson_in.get("order", 0)
    )
    db.add(lesson)
    db.flush()

    # Optional: create assessments if provided (use your existing _upsert_assessment or create_assessment)
    # Fixed signature call with empty state trackers to prevent type crashes
    dummy_choice_tracker = []
    for ass_in in lesson_in.get("assessments", []):
        # Use your existing upsert helper if it is accessible here
        # If the helper is private (prefixed with _), you can call it:
        _upsert_assessment(db, lesson, ass_in, dummy_choice_tracker)  # reuse existing helper
        # _upsert_assessment flushes and returns the assessment

    db.commit()
    db.refresh(lesson)
    return lesson

def delete_lesson_simple(db: Session, lesson_id: int):
    """
    Delete a lesson and cascade-clean related entities:
    - StudentLesson (progress)
    - AssessmentAttempt and StudentAnswer
    - Choice and Assessment
    """
    # delete student lesson completions
    db.query(models.StudentLesson).filter_by(lesson_id=lesson_id).delete(synchronize_session=False)

    # gather associated assessment ids
    ass_ids = [a.id for a in db.query(models.Assessment).filter_by(lesson_id=lesson_id).all()]

    if ass_ids:
        # student answers referencing choices/attempts
        # delete StudentAnswer rows referencing attempts for safety
        # first delete answers that reference attempts (attempts will be deleted next)
        # note: your existing code sometimes did StudentAnswer.filter(attempt_id==aid) - consistent approach:
        db.query(models.StudentAnswer).filter(models.StudentAnswer.attempt_id.in_(
            db.query(models.AssessmentAttempt.id).filter(models.AssessmentAttempt.assessment_id.in_(ass_ids))
        )).delete(synchronize_session=False)

        # delete AssessmentAttempt rows
        db.query(models.AssessmentAttempt).filter(models.AssessmentAttempt.assessment_id.in_(ass_ids)).delete(synchronize_session=False)

        # delete StudentAnswer rows that reference choice ids (if any remain)
        db.query(models.StudentAnswer).filter(models.StudentAnswer.choice_id.in_(
            db.query(models.Choice.id).filter(models.Choice.assessment_id.in_(ass_ids))
        )).delete(synchronize_session=False)

        # delete choice rows
        db.query(models.Choice).filter(models.Choice.assessment_id.in_(ass_ids)).delete(synchronize_session=False)

        # delete assessment rows
        db.query(models.Assessment).filter(models.Assessment.id.in_(ass_ids)).delete(synchronize_session=False)

    # finally delete lesson
    db.query(models.Lesson).filter_by(id=lesson_id).delete(synchronize_session=False)

    db.flush()
    return True

def update_course_structure(db, course_id, sections, instructor_id):
    course = db.query(models.Course).filter_by(
        id=course_id,
        educator_id=instructor_id
    ).first()

    if not course:
        raise HTTPException(404, "Course not found")

    existing_sections = {s.id: s for s in course.sections}
    seen_section_ids = set()

    for sec in sections:
        if sec.id and sec.id in existing_sections:
            section = existing_sections[sec.id]
            section.title = sec.title
            section.order = sec.order
        else:
            section = models.Section(
                course_id=course.id,
                title=sec.title,
                order=sec.order,
            )
            db.add(section)
            db.flush()

        seen_section_ids.add(section.id)

        existing_lessons = {l.id: l for l in section.lessons}
        seen_lesson_ids = set()

        for les in sec.lessons:
            if les.id and les.id in existing_lessons:
                lesson = existing_lessons[les.id]
                lesson.title = les.title
                lesson.type = les.type
                lesson.youtube_url = les.youtube_url
                lesson.pdf_url = les.pdf_url
                lesson.order = les.order
            else:
                lesson = models.Lesson(
                    section_id=section.id,
                    title=les.title,
                    type=les.type,
                    youtube_url=les.youtube_url,
                    pdf_url=les.pdf_url,
                    order=les.order,
                )
                db.add(lesson)
                db.flush()

            seen_lesson_ids.add(lesson.id)

        # delete removed lessons
        for lid in existing_lessons.keys():
            if lid not in seen_lesson_ids:
                delete_lesson_simple(db, lesson_id=lid)
                

    # delete removed sections
    for sid, section in existing_sections.items():
        if sid not in seen_section_ids:
            # Clean all child lessons inside the deleted section first
            for lesson in section.lessons:
                delete_lesson_simple(db, lesson_id=lesson.id)
            db.delete(section)

    db.commit()
    return {"ok": True}

# Feedback

def can_give_feedback(db: Session, user_id: int, course_id: int) -> bool:
    enrollment = db.query(models.Enrollment).filter_by(
        user_id=user_id, course_id=course_id
    ).first()
    return bool(enrollment and enrollment.progress_percent >= 25)

####

def upsert_feedback(db: Session, user_id: int, course_id: int, fb: schemas.FeedbackCreate):
    feedback = db.query(models.CourseFeedback).filter_by(
        user_id=user_id, course_id=course_id
    ).first()

    if feedback:
        feedback.rating = fb.rating
        feedback.comment_markdown = fb.comment_markdown
    else:
        feedback = models.CourseFeedback(
            user_id=user_id,
            course_id=course_id,
            rating=fb.rating,
            comment_markdown=fb.comment_markdown
        )
        db.add(feedback)

    db.commit()
    db.refresh(feedback)
    return feedback

def list_feedback_for_course(db: Session, course_id: int, limit: int = 50, offset=0):
    rows = (
        db.query(models.CourseFeedback, models.User.full_name).join(models.User, models.User.id == models.CourseFeedback.user_id).filter(
            models.CourseFeedback.course_id == course_id).filter(models.CourseFeedback.rating.isnot(None)).order_by(models.CourseFeedback.created_at.desc()).offset(offset).limit(limit).all()
    )
    #return db.query(models.CourseFeedback).filter_by(course_id=course_id).order_by(
    #    models.CourseFeedback.created_at.desc()
    #).offset(offset).limit(limit).all()
    
    return [
        schemas.FeedbackOut(
            id=fb.id,
            rating=fb.rating,
            comment_markdown=fb.comment_markdown,
            created_at=fb.created_at,
            user_name=full_name,
            user_id=fb.user_id,
            course_id=fb.course_id
        )
        for fb, full_name in rows
    ]

def get_feedback_summary(db: Session, course_id: int):
    from sqlalchemy import func
    avg_rating = db.query(func.avg(models.CourseFeedback.rating)).filter(models.CourseFeedback.course_id == course_id, models.CourseFeedback.rating.isnot(None)).scalar()
    count = db.query(func.count(models.CourseFeedback.id)).filter(models.CourseFeedback.course_id == course_id).scalar()
    return {
        "avg_rating": round(avg_rating or 0, 2),
        "total_reviews": count
    }


def get_instructor_course_stats(db: Session, instructor_id: int, course_id: int):
    #ownership courses
    course = db.query(models.Course).filter(models.Course.id == course_id, models.Course.educator_id == instructor_id).first()
    if not course:
        print("Course :" + course_id + " not found or not owned by instructor")
        return None
    enrollment_count = db.query(func.count(models.Enrollment.id)).filter(models.Enrollment.course_id == course_id).scalar()
    #feedback_count = db.query(func.count(models.CourseFeedback.id)).filter(models.CourseFeedback.course_id == course_id).scalar()
    #avg_rating = db.query(func.avg(models.CourseFeedback.rating)).filter(models.CourseFeedback.course_id == course_id, models.CourseFeedback.rating.isnot(None)).scalar()
    #feedback_list = list_feedback_for_course(db, course_id, limit=5, offset=0)
    return {
        "enrollment_count": enrollment_count
    }
    

def get_public_feedback(db: Session, course_id: int, limit: int = 10):
    rows = (
        db.query(models.CourseFeedback, models.User.full_name)
        .join(models.User, models.User.id == models.CourseFeedback.user_id)
        .filter(models.CourseFeedback.course_id == course_id)
        .filter(models.CourseFeedback.rating.isnot(None))
        .order_by(models.CourseFeedback.created_at.desc())
        .limit(limit)
        .all()
    )

    reviews = [
        schemas.FeedbackPublicOut(
            id=fb.id,
            rating=fb.rating,
            comment_markdown=fb.comment_markdown,
            user_name=full_name,
            created_at=fb.created_at
        )
        for fb, full_name in rows
    ]

    avg_rating = (
        db.query(func.avg(models.CourseFeedback.rating))
        .filter(models.CourseFeedback.course_id == course_id)
        .scalar()
    )

    total = (
        db.query(models.CourseFeedback.id)
        .filter(models.CourseFeedback.course_id == course_id)
        .count()
    )

    return {
        "avg_rating": round(avg_rating or 0, 2),
        "total_ratings": total,
        "reviews": reviews
    }




def get_successful_payment(db: Session, user_id: int, course_id: int):
    return (
        db.query(models.Payment)
        .filter(
            models.Payment.user_id == user_id,
            models.Payment.course_id == course_id,
            models.Payment.status == "success",
        )
        .order_by(models.Payment.created_at.desc())
        .first()
    )

#def add_feedback(db: Session, f: schemas.FeedbackCreate):
#    fb = models.CourseFeedback(user_id=f.user_id, course_id=f.course_id, rating=f.rating, comment_markdown=f.comment_markdown)
#    db.add(fb); db.commit(); db.refresh(fb)
#    return fb