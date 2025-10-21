from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.course import Course
from app.schemas.category import (
    CategoryCreate, CategoryUpdate,
    CategoryResponse, CategoryShort
)
from app.utils.dependencies import get_current_user, require_role

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
        db: Session = Depends(get_db)
):
    """Получение всех категорий"""

    categories = db.query(Category).order_by(Category.order, Category.name).all()

    # Добавляем количество курсов для каждой категории
    result = []
    for category in categories:
        courses_count = db.query(func.count(Course.id)).filter(
            Course.category_id == category.id,
            Course.is_published == True
        ).scalar()

        category_dict = {
            **category.__dict__,
            "courses_count": courses_count
        }
        result.append(CategoryResponse(**category_dict))

    return result


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
        category_id: int,
        db: Session = Depends(get_db)
):
    """Получение категории по ID"""

    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    courses_count = db.query(func.count(Course.id)).filter(
        Course.category_id == category.id,
        Course.is_published == True
    ).scalar()

    return CategoryResponse(
        **category.__dict__,
        courses_count=courses_count
    )


@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
        slug: str,
        db: Session = Depends(get_db)
):
    """Получение категории по slug"""

    category = db.query(Category).filter(Category.slug == slug).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    courses_count = db.query(func.count(Course.id)).filter(
        Course.category_id == category.id,
        Course.is_published == True
    ).scalar()

    return CategoryResponse(
        **category.__dict__,
        courses_count=courses_count
    )


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
        category_data: CategoryCreate,
        current_user: User = Depends(require_role([UserRole.ADMIN])),
        db: Session = Depends(get_db)
):
    """Создание новой категории (только для админов)"""

    # Проверка уникальности имени
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    # Проверка уникальности slug
    existing_slug = db.query(Category).filter(Category.slug == category_data.slug).first()
    if existing_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this slug already exists"
        )

    new_category = Category(**category_data.model_dump())

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return CategoryResponse(**new_category.__dict__, courses_count=0)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
        category_id: int,
        category_data: CategoryUpdate,
        current_user: User = Depends(require_role([UserRole.ADMIN])),
        db: Session = Depends(get_db)
):
    """Обновление категории (только для админов)"""

    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    update_data = category_data.model_dump(exclude_unset=True)

    # Проверка уникальности имени
    if "name" in update_data:
        existing = db.query(Category).filter(
            Category.name == update_data["name"],
            Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )

    # Проверка уникальности slug
    if "slug" in update_data:
        existing_slug = db.query(Category).filter(
            Category.slug == update_data["slug"],
            Category.id != category_id
        ).first()
        if existing_slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this slug already exists"
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    courses_count = db.query(func.count(Course.id)).filter(
        Course.category_id == category.id,
        Course.is_published == True
    ).scalar()

    return CategoryResponse(**category.__dict__, courses_count=courses_count)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
        category_id: int,
        current_user: User = Depends(require_role([UserRole.ADMIN])),
        db: Session = Depends(get_db)
):
    """Удаление категории (только для админов)"""

    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Проверка, есть ли курсы в этой категории
    courses_count = db.query(func.count(Course.id)).filter(
        Course.category_id == category_id
    ).scalar()

    if courses_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with {courses_count} courses. Move courses first."
        )

    db.delete(category)
    db.commit()

    return None