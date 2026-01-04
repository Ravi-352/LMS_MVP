from pydantic import BaseModel, EmailStr, SecretStr, Field
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
    question_markdown: str = ""
    image_url: Optional[str] = None
    max_score: Optional[int] = 1
    explanation: Optional[str] = None
    #choices: Optional[List[ChoiceCreate]] = []
    choices: Optional[List[ChoiceCreate]] = None


class AssessmentUpdate(BaseModel):
    id: Optional[int] = None
    lesson_id: Optional[int] = None
    question_markdown: str
    image_url: Optional[str] = None
    max_score: Optional[int] = 1
    explanation: Optional[str] = None
    #choices: Optional[List[ChoiceCreate]] = []
    choices: Optional[List[ChoiceCreate]] = None

class AssessmentOut(BaseModel):
    id: int
    question_markdown: str
    image_url: Optional[str] = None
    max_score: int
    explanation: Optional[str] = None
    choices: List[ChoiceOut] = []
    class Config:
        orm_mode = True

class LessonUpsert(BaseModel):
    id: int | None = None
    title: str
    type: str
    youtube_url: str | None = None
    pdf_url: str | None = None
    order: int

class SectionUpsert(BaseModel):
    id: int | None = None
    title: str
    order: int
    lessons: list[LessonUpsert] = []

class CourseStructureUpdate(BaseModel):
    sections: list[SectionUpsert]


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
    title: Optional[str] = None
    type: Optional[str] = None  # "video" or "pdf"
    youtube_url: Optional[str] = None
    pdf_url: Optional[str] = None
    order: Optional[int] = 0
    #assessments: Optional[List[AssessmentCreate]] = []
    assessments: Optional[List[AssessmentCreate]] = None

class LessonUpdate(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    type: Optional[str] = None
    youtube_url: Optional[str] = None
    pdf_url: Optional[str] = None
    order: Optional[int] = None
    assessments: Optional[List["AssessmentUpdate"]] = None


class SectionCreate(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    order: Optional[int] = 0
    #lessons: Optional[List[LessonCreate]] = []
    lessons: Optional[List[LessonCreate]] = None


class SectionUpdate(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    order: Optional[int] = None
    lessons: Optional[List[LessonUpdate]] = None


class CourseCreate(BaseModel):
    title: str
    #slug: Optional[str] = None
    description: Optional[str] = None
    #is_udemy: Optional[bool] = False
    is_udemy: bool = False
    udemy_url: Optional[str] = None
    price_cents: Optional[int] = None
    currency: Optional[str] = None
    #sections: Optional[List[SectionCreate]] = []

#class CourseUpdate(CourseCreate):
    #id: Optional[int] = None  # optional for update if you want

class CourseUpdate(BaseModel):
    id: Optional[int] = None  # optional for update if you want
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    is_udemy: Optional[bool] = None
    udemy_url: Optional[str] = None
    price_cents: Optional[int] = 0
    currency: Optional[str] = "INR"
    sections: Optional[List["SectionUpdate"]] = None



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

class LessonEditorOut(BaseModel):
    id: int
    title: str
    type: str
    order: int

    class Config:
        from_attributes = True


class SectionEditorOut(BaseModel):
    id: int
    title: str
    order: int
    lessons: List[LessonEditorOut]

    class Config:
        from_attributes = True

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
    price_cents: int
    currency: str
    sections: List[SectionOut] = []

    class Config:
        orm_mode = True

class CourseListOut(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str]
    is_udemy: bool
    udemy_url: Optional[str]
    price_cents: Optional[int] = None
    currency: Optional[str] = None

    class Config:
        orm_mode = True

class StudentCourseOut(BaseModel):
    course_id: int
    course_title: str
    course_slug: str
    course_description: Optional[str]
    progress_percent: float
    status: str
    is_udemy: bool
    udemy_url: Optional[str]

    class Config:
        #from_attributes = True
        orm_mode = True

class StudentCourseStateOut(BaseModel):
    is_enrolled: bool
    progress_percent: float
    completed_lesson_ids: list[int]

    class Config:
        orm_mode = True



class PublicCourseListOut(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str]
    is_udemy: bool
    udemy_url: Optional[str]
    price_cents: Optional[int] = None
    currency: Optional[str] = None

    class Config:
        orm_mode = True


class CourseEditorOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price_cents: int
    currency: str
    is_published: bool
    sections: List[SectionEditorOut]

    class Config:
        #from_attributes = True
        orm_mode = True


# Enrollment
#EnrollmentCreate should be deleted because the client must NEVER tell the backend who is enrolling.
#That information must come from authentication, not request body.
#class EnrollmentCreate(BaseModel):
#    user_id: int
#    course_id: int
class EnrollmentCreate(BaseModel):
    course_id: int
    
class EnrollmentOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    progress_percent: float
    status: str

    class Config:
        orm_mode = True

class EnrollmentAttemptOut(BaseModel):
    requires_payment: bool
    course_id: int


# Payments
class CoursePriceOut(BaseModel):
    currency: str
    amount_cents: int
    is_free: bool

class PaymentOut(BaseModel):
    id: int
    provider: str
    amount_cents: int
    currency: str
    status: str
    created_at: datetime








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
    # Client cannot impersonate another user - user_id will come from auth context. not from frontend. 
    # Course ID already comes from the URL path
    #user_id: int
    #course_id: int
    rating: Optional[int] = Field(None, ge=1, le=5)
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

class OkResponse(BaseModel):
    ok: bool = True


# ---- Forward Reference Fix ----
LessonCreate.update_forward_refs()
LessonOut.update_forward_refs()
LessonUpdate.update_forward_refs()
SectionUpdate.update_forward_refs()
CourseUpdate.update_forward_refs()
