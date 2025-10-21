from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.course import CourseLevel, CourseStatus


# Базовая схема курса
class CourseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    short_description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    level: CourseLevel = CourseLevel.BEGINNER
    language: str = "ru"
    price: float = Field(0.0, ge=0)
    discount_price: Optional[float] = Field(None, ge=0)
    currency: str = "USD"
    requirements: Optional[str] = None
    learning_outcomes: Optional[str] = None
    target_audience: Optional[str] = None
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None

    @field_validator('discount_price')
    @classmethod
    def validate_discount(cls, v, info):
        if v is not None and 'price' in info.data:
            if v >= info.data['price']:
                raise ValueError('Discount price must be less than regular price')
        return v


# Схема для создания курса
class CourseCreate(CourseBase):
    pass


# Схема для обновления курса
class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    short_description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    level: Optional[CourseLevel] = None
    language: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    discount_price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    requirements: Optional[str] = None
    learning_outcomes: Optional[str] = None
    target_audience: Optional[str] = None
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    status: Optional[CourseStatus] = None


# Схема для публикации курса
class CoursePublish(BaseModel):
    is_published: bool


# Схема краткой информации о курсе (для списков)
class CourseShort(BaseModel):
    id: int
    title: str
    short_description: Optional[str]
    thumbnail_url: Optional[str]
    level: CourseLevel
    price: float
    discount_price: Optional[float]
    average_rating: float
    total_students: int
    total_lessons: int
    duration_hours: float
    instructor_name: str
    category_name: Optional[str] = None
    is_free: bool

    model_config = ConfigDict(from_attributes=True)


# Полная схема курса
class CourseResponse(CourseBase):
    id: int
    slug: str
    status: CourseStatus
    is_published: bool
    instructor_id: int
    instructor_name: str
    instructor_avatar: Optional[str] = None
    category_name: Optional[str] = None
    duration_hours: float
    total_students: int
    average_rating: float
    total_reviews: int
    total_lessons: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    is_free: bool
    effective_price: float

    model_config = ConfigDict(from_attributes=True)


# Схема для списка курсов с пагинацией
class CourseList(BaseModel):
    courses: List[CourseShort]
    total: int
    page: int
    page_size: int
    total_pages: int


# Схема для фильтрации курсов
class CourseFilter(BaseModel):
    search: Optional[str] = None
    category_id: Optional[int] = None
    level: Optional[CourseLevel] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    is_free: Optional[bool] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    instructor_id: Optional[int] = None
    status: Optional[CourseStatus] = None

    # Сортировка
    sort_by: str = "created_at"  # created_at, price, rating, students
    sort_order: str = "desc"  # asc, desc

    # Пагинация
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)