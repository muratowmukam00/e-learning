from typing import Optional, List
from pydantic import BaseModel, Field, validator, field_validator
from datetime import datetime
from app.models.lesson import LessonType


class LessonBase(BaseModel):
    """Базовая схема урока"""
    title: str = Field(..., min_length=3, max_length=255, description="Название урока")
    description: Optional[str] = Field(None, description="Описание урока")
    lesson_type: LessonType = Field(default=LessonType.VIDEO, description="Тип урока")
    content: Optional[str] = Field(None, description="Текстовый контент урока (HTML/Markdown)")
    video_url: Optional[str] = Field(None, description="URL видео")
    video_duration: Optional[float] = Field(None, ge=0, description="Длительность видео в минутах")
    resources_urls: Optional[str] = Field(None, description="JSON список ресурсов для скачивания")
    is_free_preview: bool = Field(default=False, description="Бесплатный предпросмотр")
    is_published: bool = Field(default=True, description="Опубликован ли урок")


class LessonCreate(LessonBase):
    """Схема для создания урока"""
    course_id: int = Field(..., gt=0, description="ID курса")
    order: Optional[int] = Field(None, ge=1, description="Порядковый номер урока")

    @field_validator('video_url')
    def validate_video_url(cls, v, info):
        """Проверка URL видео для VIDEO типа"""
        if info.data.get('lesson_type') == LessonType.VIDEO and not v:
            raise ValueError('video_url обязателен для видео-уроков')
        return v

    @field_validator('content')
    def validate_content(cls, v, info):
        """Проверка контента для TEXT типа"""
        if info.data.get('lesson_type') == LessonType.TEXT and not v:
            raise ValueError('content обязателен для текстовых уроков')
        return v


class LessonUpdate(BaseModel):
    """Схема для обновления урока"""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    lesson_type: Optional[LessonType] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    video_duration: Optional[float] = Field(None, ge=0)
    resources_urls: Optional[str] = None
    is_free_preview: Optional[bool] = None
    is_published: Optional[bool] = None
    order: Optional[int] = Field(None, ge=1)

    class Config:
        use_enum_values = True


class LessonResponse(LessonBase):
    """Схема ответа с информацией об уроке"""
    id: int
    course_id: int
    order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True


class LessonDetail(LessonResponse):
    """Детальная информация об уроке (включая контент)"""
    pass


class LessonWithProgress(LessonResponse):
    """Урок с информацией о прогрессе студента"""
    is_completed: bool = False
    completion_percentage: float = 0.0
    time_spent: int = 0  # в секундах

    class Config:
        from_attributes = True


class LessonListResponse(BaseModel):
    """Список уроков с общей информацией"""
    total: int
    lessons: List[LessonResponse]


class ReorderLessonRequest(BaseModel):
    """Запрос на изменение порядка урока"""
    new_order: int = Field(..., ge=1, description="Новый порядковый номер")