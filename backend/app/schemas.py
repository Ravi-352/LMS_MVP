from pydantic import BaseModel, EmailStr, SecretStr
from typing import Optional, List
from datetime import datetime



# --- Choice schemas ---
class ChoiceCreate(BaseModel):
    id: Optional[int] = None
    text: str
    is_correct: Optional[bool] = False
    explanation: Optional[str] = None

#class ChoiceCreate(BaseModel):
#    assessment_id: int
#    text: str
#    is_correct: bool = False

class ChoiceOut(BaseModel):
    id: int
    text: str
    # don't return is_correct to students; only instructors should see correct flags
    explanation: Optional[str] = None
    class Config:
        orm_mode = True


# --- Assessment schemas ---
class AssessmentCreate(BaseModel):
    id: Optional[int] = None
    lesson_id: Optional[int] = None
    question_markdown: str
    image_url: Optional[str] = None
    max_score: Optional[int] = 1
    explanation: Optional[str] = None
    choices: List[ChoiceCreate] = []

class AssessmentOut(BaseModel):
    id: int
    question_markdown: str
    image_url: Optional[str] = None
    max_score: int
    explanation: Optional[str] = None
    choices: List[ChoiceOut] = []
    class Config:
        orm_mode = True

# Assessment - for students hide correct answers
class AssessmentQuestionOut(BaseModel):
    id: int
    question_markdown: str
    image_url: Optional[str] = None
    max_score: int
    explanation: Optional[str] = None  # can be omitted for students until they submit
    choices: List[ChoiceOut] = []

    class Config:
        orm_mode = True

# User schemas
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    is_educator: bool = False
    #full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_educator: bool

    class Config:
        orm_mode = True

# Course / Section / Lesson
class LessonCreate(BaseModel):
    id: Optional[int] = None
    title: str
    type: str  # "video" or "pdf"
    youtube_url: Optional[str] = None
    pdf_url: Optional[str] = None
    order: Optional[int] = 0
    assessments: List[AssessmentCreate] = []

class SectionCreate(BaseModel):
    id: Optional[int] = None
    title: str
    order: Optional[int] = 0
    lessons: Optional[List[LessonCreate]] = []

class CourseCreate(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    is_udemy: Optional[bool] = False
    udemy_url: Optional[str] = None
    sections: Optional[List[SectionCreate]] = []

class CourseUpdate(CourseCreate):
    id: Optional[int] = None  # optional for update if you want

class LessonOut(BaseModel):
    id: int
    title: str
    type: str
    youtube_url: Optional[str] = None
    pdf_url: Optional[str] = None
    order: int
    assessments: Optional[List[AssessmentQuestionOut]] = []

    class Config:
        orm_mode = True


class SectionOut(BaseModel):
    id: int
    title: str
    order: int
    lessons: List[LessonOut] = []

    class Config:
        orm_mode = True


#class CourseOut(BaseModel):
#    id: int
#    title: str
#    slug: str
#    description: Optional[str]
#    is_udemy: bool
#    udemy_url: Optional[str]

#    class Config:
#        orm_mode = True

# Course detail (APEX)
class CourseDetailOut(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str]
    is_udemy: bool
    udemy_url: Optional[str]
    sections: List[SectionOut] = []

    class Config:
        orm_mode = True

# Enrollment
class EnrollmentCreate(BaseModel):
    user_id: int
    course_id: int

class EnrollmentOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    progress_percent: float
    status: str

    class Config:
        orm_mode = True







#class AssessmentCreate(BaseModel):
#    lesson_id: Optional[int]
#    question_markdown: str
#    image_url: Optional[str] = None




# Assessment attempt result returned to student
class QuestionResult(BaseModel):
    question_id: int
    selected_choice_id: Optional[int] = None
    is_correct: bool
    correct_choice_id: Optional[int] = None
    score: float
    explanation: Optional[str] = None

class AttemptResultOut(BaseModel):
    attempt_id: int
    assessment_id: int
    attempt_number: int
    total_score: float
    question_results: List[QuestionResult] = []

    class Config:
        orm_mode = True

# Feedback
class FeedbackCreate(BaseModel):
    user_id: int
    course_id: int
    rating: Optional[int] = None
    comment_markdown: Optional[str] = None

class FeedbackOut(BaseModel):
    id: int
    rating: int
    comment: Optional[str]
    user_id: int
    course_id: int
    created_at: datetime
    class Config:
        orm_mode = True

# ---- Forward Reference Fix ----
LessonCreate.update_forward_refs()
LessonOut.update_forward_refs()