from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProgressBase(BaseModel):
    """Базовая схема прогресса"""
    is_completed: bool = False
    completion_percentage: float = Field(0.0, ge=0.0, le=100.0)
    time_spent: int = Field(0, ge=0)  # в секундах


class ProgressCreate(ProgressBase):
    """Создание записи прогресса"""
    lesson_id: int


class ProgressUpdate(BaseModel):
    """Обновление прогресса"""
    is_completed: Optional[bool] = None
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    time_spent: Optional[int] = Field(None, ge=0)


class ProgressResponse(ProgressBase):
    """Ответ с данными прогресса"""
    id: int
    student_id: int
    lesson_id: int
    started_at: datetime
    completed_at: Optional[datetime]
    last_accessed_at: datetime

    class Config:
        from_attributes = True


class LessonProgressResponse(BaseModel):
    """Прогресс по конкретному уроку"""
    lesson_id: int
    lesson_title: str
    lesson_order: int
    is_completed: bool
    completion_percentage: float
    time_spent: int
    last_accessed_at: datetime

    class Config:
        from_attributes = True


class CourseProgressSummary(BaseModel):
    """Сводка по прогрессу курса"""
    course_id: int
    course_title: str
    total_lessons: int
    completed_lessons: int
    progress_percentage: float
    total_time_spent: int  # в секундах
    enrolled_at: datetime
    last_accessed_at: Optional[datetime]

    class Config:
        from_attributes = True


class StudentStatistics(BaseModel):
    """Статистика студента"""
    total_enrolled_courses: int
    completed_courses: int
    in_progress_courses: int
    total_lessons_completed: int
    total_time_spent: int  # в секундах
    average_progress: float  # средний процент прогресса по всем курсам

    class Config:
        from_attributes = True