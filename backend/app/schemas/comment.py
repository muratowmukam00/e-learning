from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CommentBase(BaseModel):
    """Базовая схема комментария"""
    content: str = Field(..., min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    """Создание комментария"""
    lesson_id: int
    parent_id: Optional[int] = None  # Для ответов на комментарии


class CommentUpdate(BaseModel):
    """Обновление комментария"""
    content: str = Field(..., min_length=1, max_length=2000)


class UserBrief(BaseModel):
    """Краткая информация о пользователе"""
    id: int
    first_name: str
    last_name: str
    avatar_url: Optional[str]
    role: str

    class Config:
        from_attributes = True


class CommentResponse(CommentBase):
    """Ответ с данными комментария"""
    id: int
    user_id: int
    lesson_id: int
    parent_id: Optional[int]
    is_edited: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    # Информация об авторе
    user: UserBrief

    # Количество ответов
    replies_count: int = 0

    class Config:
        from_attributes = True


class CommentWithReplies(CommentResponse):
    """Комментарий с вложенными ответами"""
    replies: List['CommentResponse'] = []

    class Config:
        from_attributes = True


# Для корректной работы рекурсивных моделей
CommentWithReplies.model_rebuild()


class LessonCommentsResponse(BaseModel):
    """Список комментариев урока"""
    lesson_id: int
    total_comments: int
    comments: List[CommentWithReplies]