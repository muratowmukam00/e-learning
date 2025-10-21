from typing import Optional, Dict
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ReviewBase(BaseModel):
    """Базовая схема отзыва"""
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5 звезд")
    title: Optional[str] = Field(None, max_length=200, description="Заголовок отзыва")
    comment: Optional[str] = Field(None, description="Текст отзыва")


class ReviewCreate(ReviewBase):
    """Схема для создания отзыва"""
    course_id: int = Field(..., gt=0, description="ID курса")

    @validator('comment')
    def comment_not_empty_if_provided(cls, v):
        """Если комментарий указан, он не должен быть пустым"""
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Комментарий не может быть пустым')
        return v


class ReviewUpdate(BaseModel):
    """Схема для обновления отзыва"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = None

    @validator('comment')
    def comment_not_empty_if_provided(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Комментарий не может быть пустым')
        return v


class ReviewResponse(ReviewBase):
    """Схема ответа с информацией об отзыве"""
    id: int
    student_id: int
    course_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewWithUser(ReviewResponse):
    """Отзыв с информацией о пользователе"""
    student_name: str
    student_avatar: Optional[str] = None


class ReviewStats(BaseModel):
    """Статистика отзывов курса"""
    course_id: int
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[str, int] = Field(
        description="Распределение оценок: {'5': 10, '4': 5, '3': 2, '2': 1, '1': 0}"
    )


class CourseWithReviews(BaseModel):
    """Курс с отзывами"""
    id: int
    title: str
    average_rating: float
    total_reviews: int
    reviews: list[ReviewWithUser]

    class Config:
        from_attributes = True


class CheckReviewResponse(BaseModel):
    """Ответ на проверку наличия отзыва"""
    has_review: bool
    review: Optional[ReviewResponse] = None