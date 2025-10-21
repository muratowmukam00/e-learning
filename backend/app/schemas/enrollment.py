from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.enrollment import EnrollmentStatus


class EnrollmentBase(BaseModel):
    """Базовая схема для записи на курс"""
    course_id: int = Field(..., gt=0, description="ID курса")


class EnrollmentCreate(EnrollmentBase):
    """Схема для создания записи на курс"""
    pass


class EnrollmentResponse(BaseModel):
    """Схема ответа с информацией о записи"""
    id: int
    student_id: int
    course_id: int
    status: EnrollmentStatus
    progress_percentage: float
    completed_lessons: int
    price_paid: float
    is_paid: bool
    enrolled_at: datetime
    last_accessed_at: datetime
    completed_at: Optional[datetime] = None
    certificate_url: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class EnrollmentDetail(EnrollmentResponse):
    """Детальная информация о записи"""
    certificate_issued_at: Optional[datetime] = None


class CourseInfo(BaseModel):
    """Краткая информация о курсе"""
    id: int
    title: str
    slug: str
    thumbnail_url: Optional[str]
    level: str
    total_lessons: int
    duration_hours: float
    instructor_name: str

    class Config:
        from_attributes = True


class EnrollmentWithCourse(EnrollmentResponse):
    """Запись с информацией о курсе"""
    course: CourseInfo


class StudentInfo(BaseModel):
    """Информация о студенте"""
    id: int
    full_name: str
    email: str
    avatar_url: Optional[str]


class StudentListResponse(BaseModel):
    """Ответ со списком студентов курса"""
    enrollment_id: int
    student_id: int
    student_name: str
    student_email: str
    student_avatar: Optional[str]
    progress_percentage: float
    completed_lessons: int
    status: EnrollmentStatus
    enrolled_at: datetime
    last_accessed_at: datetime

    class Config:
        use_enum_values = True


class EnrollmentStats(BaseModel):
    """Статистика записей на курс"""
    course_id: int
    course_title: str
    total_enrollments: int
    active_students: int
    completed_students: int
    dropped_students: int
    average_progress: float
    completion_rate: float


class CheckEnrollmentResponse(BaseModel):
    """Ответ на проверку записи"""
    is_enrolled: bool
    has_access: bool
    progress_percentage: Optional[float] = None
    status: Optional[EnrollmentStatus] = None

    class Config:
        use_enum_values = True