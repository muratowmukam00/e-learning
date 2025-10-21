from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# Базовая схема категории
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    order: int = 0


# Схема для создания категории
class CategoryCreate(CategoryBase):
    pass


# Схема для обновления категории
class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    order: Optional[int] = None


# Схема ответа категории
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    courses_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# Краткая схема категории
class CategoryShort(BaseModel):
    id: int
    name: str
    slug: str
    icon: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)