from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, text, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime, func
from datetime import datetime, timezone
from app.db.base import Base

# This file defines your database structure using SQLAlchemy ORM
# Each class = a database table.
# Each attribute = a database column
# Relationships = table connections (foreign keys)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    google_id = Column(String, nullable=True, unique=True)
    is_educator = Column(Boolean, default=False)
    #created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    #created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
    # Flags to identify login method
    is_google_account = Column(Boolean, default=False)
    

    enrollments = relationship("Enrollment", back_populates="user")
    feedbacks = relationship("CourseFeedback", back_populates="user")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="user")
    student_lessons = relationship("StudentLesson", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user")


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    educator_id = Column(Integer, ForeignKey("users.id"), nullable=False) # NEW COLUMN
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_udemy = Column(Boolean, default=False)
    udemy_url = Column(String, nullable=True)
    price_cents = Column(Integer, default=0, nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
     # optional
    is_published = Column(Boolean, default=True)
    #created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    #created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # sections = relationship("Section", back_populates="course")
    educator = relationship("User", backref="courses")  # NEW RELATION
    enrollments = relationship("Enrollment", back_populates="course")
    feedbacks = relationship("CourseFeedback", back_populates="course")
    sections = relationship("Section", back_populates="course", cascade="all, delete-orphan", lazy="selectin")
    payments = relationship("Payment", back_populates="course")


class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    order = Column(Integer, default=0)

    #relationships
    course = relationship("Course", back_populates="sections")
    # lessons = relationship("Lesson", back_populates="section")
    lessons = relationship("Lesson", back_populates="section", cascade="all, delete-orphan", lazy="selectin")

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "video" or "pdf"
    youtube_url = Column(String, nullable=True)
    pdf_url = Column(String, nullable=True)
    order = Column(Integer, default=0)

    section = relationship("Section", back_populates="lessons")
    assessments = relationship("Assessment", back_populates="lesson", cascade="all, delete-orphan", lazy="selectin")
    student_lessons = relationship("StudentLesson", back_populates="lesson", cascade="all, delete-orphan")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    progress_percent = Column(Float, default=0.0)
    status = Column(String, default="enrolled")  # enrolled | completed

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course"),
    )
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    question_markdown = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    max_score = Column(Integer, default=1)
    explanation = Column(Text, nullable=True)
    # relationships
    # choices = relationship("Choice", back_populates="assessment")
    choices = relationship("Choice",  back_populates="assessment", cascade="all, delete-orphan")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="assessment", cascade="all, delete-orphan")
    # Must match back_populates in Lesson
    lesson = relationship("Lesson", back_populates="assessments")

class Choice(Base):
    __tablename__ = "choices"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)
    explanation = Column(Text, nullable=True)
    # relationships
    assessment = relationship("Assessment", back_populates="choices")
    answers = relationship("StudentAnswer", back_populates="choice", cascade="all, delete-orphan")


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    attempt_number = Column(Integer, default=1)
    score = Column(Float, default=0.0)
    #created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # relationship: answers will reference this attempt
    user = relationship("User", back_populates="assessment_attempts")
    assessment = relationship("Assessment", back_populates="assessment_attempts")
    answers = relationship("StudentAnswer", back_populates="assessment_attempts", cascade="all, delete-orphan")


class StudentAnswer(Base):
    __tablename__ = "student_answers"
    id = Column(Integer, primary_key=True, index=True)
    #user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    #assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    choice_id = Column(Integer, ForeignKey("choices.id"), nullable=True)
    #created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    attempt_id = Column(Integer, ForeignKey("assessment_attempts.id"), nullable=False)
    is_correct = Column(Boolean, default=False)
    score = Column(Float, default=0.0)
    #relationships
    #attempt = relationship("AssessmentAttempt", back_populates="answers")
    choice = relationship("Choice", back_populates="answers")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="answers")


class CourseFeedback(Base):
    __tablename__ = "course_feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 optional
    comment_markdown = Column(Text, nullable=True)
    #created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    #created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_feedback"),
    )

    user = relationship("User", back_populates="feedbacks")
    course = relationship("Course", back_populates="feedbacks")

class StudentLesson(Base):
    __tablename__ = "student_lessons"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), primary_key=True)
    completed_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    # Optional relationships if you want easy access:
    user = relationship("User", back_populates="student_lessons")
    lesson = relationship("Lesson", back_populates="student_lessons")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    provider = Column(String)  # razorpay / stripe
    amount_cents = Column(Integer)
    currency = Column(String(3))
    status = Column(String)  # pending | success | failed | refunded
    provider_payment_id = Column(String)

    #created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))

     # relationships
    user = relationship("User", back_populates="payments")
    course = relationship("Course", back_populates="payments")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "course_id",
            "status",
            name="uq_payment_user_course_status"
        ),
    )
