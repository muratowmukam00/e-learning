from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import Optional, List
from datetime import datetime
import re

from app.database import get_db
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus, CourseLevel
from app.models.category import Category
from app.models.enrollment import Enrollment
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse,
    CourseList, CourseShort, CourseFilter, CoursePublish
)
from app.utils.dependencies import get_current_user, require_role

router = APIRouter(prefix="/courses", tags=["Courses"])


def generate_slug(title: str) -> str:
    """Генерация slug из названия курса"""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug


def build_course_response(course: Course, db: Session) -> dict:
    """Построение ответа с информацией о курсе"""
    instructor_name = f"{course.instructor.first_name} {course.instructor.last_name}"
    category_name = course.category.name if course.category else None

    return {
        **course.__dict__,
        "instructor_name": instructor_name,
        "instructor_avatar": course.instructor.avatar_url,
        "category_name": category_name,
        "is_free": course.is_free,
        "effective_price": course.effective_price
    }


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
        course_data: CourseCreate,
        current_user: User = Depends(require_role([UserRole.INSTRUCTOR, UserRole.ADMIN])),
        db: Session = Depends(get_db)
):
    """Создание нового курса (только для преподавателей и админов)"""

    # Проверка существования категории
    if course_data.category_id:
        category = db.query(Category).filter(Category.id == course_data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    # Генерация slug
    base_slug = generate_slug(course_data.title)
    slug = base_slug
    counter = 1

    # Проверка уникальности slug
    while db.query(Course).filter(Course.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Создание курса
    new_course = Course(
        **course_data.model_dump(),
        slug=slug,
        instructor_id=current_user.id,
        status=CourseStatus.DRAFT,
        is_published=False
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return build_course_response(new_course, db)


@router.get("/", response_model=CourseList)
async def get_courses(
        search: Optional[str] = Query(None, description="Search in title and description"),
        category_id: Optional[int] = None,
        level: Optional[CourseLevel] = None,
        min_price: Optional[float] = Query(None, ge=0),
        max_price: Optional[float] = Query(None, ge=0),
        is_free: Optional[bool] = None,
        min_rating: Optional[float] = Query(None, ge=0, le=5),
        instructor_id: Optional[int] = None,
        status: Optional[CourseStatus] = None,
        sort_by: str = Query("created_at", description="Sort by: created_at, price, rating, students"),
        sort_order: str = Query("desc", description="Sort order: asc, desc"),
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    """Получение списка курсов с фильтрацией и пагинацией"""

    # Базовый запрос
    query = db.query(Course)

    # Фильтрация по статусу (обычные пользователи видят только опубликованные)
    if not current_user or current_user.role == UserRole.STUDENT:
        query = query.filter(Course.is_published == True, Course.status == CourseStatus.PUBLISHED)
    elif status:
        query = query.filter(Course.status == status)

    # Поиск
    if search:
        search_filter = or_(
            Course.title.ilike(f"%{search}%"),
            Course.description.ilike(f"%{search}%"),
            Course.short_description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    # Фильтры
    if category_id:
        query = query.filter(Course.category_id == category_id)

    if level:
        query = query.filter(Course.level == level)

    if is_free is not None:
        if is_free:
            query = query.filter(Course.price == 0)
        else:
            query = query.filter(Course.price > 0)

    if min_price is not None:
        query = query.filter(Course.price >= min_price)

    if max_price is not None:
        query = query.filter(Course.price <= max_price)

    if min_rating is not None:
        query = query.filter(Course.average_rating >= min_rating)

    if instructor_id:
        query = query.filter(Course.instructor_id == instructor_id)

    # Сортировка
    sort_column = {
        "created_at": Course.created_at,
        "price": Course.price,
        "rating": Course.average_rating,
        "students": Course.total_students,
        "title": Course.title
    }.get(sort_by, Course.created_at)

    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Подсчет общего количества
    total = query.count()

    # Пагинация
    offset = (page - 1) * page_size
    courses = query.offset(offset).limit(page_size).all()

    # Формирование ответа
    courses_data = []
    for course in courses:
        instructor_name = f"{course.instructor.first_name} {course.instructor.last_name}"
        category_name = course.category.name if course.category else None

        courses_data.append(CourseShort(
            id=course.id,
            title=course.title,
            short_description=course.short_description,
            thumbnail_url=course.thumbnail_url,
            level=course.level,
            price=course.price,
            discount_price=course.discount_price,
            average_rating=course.average_rating,
            total_students=course.total_students,
            total_lessons=course.total_lessons,
            duration_hours=course.duration_hours,
            instructor_name=instructor_name,
            category_name=category_name,
            is_free=course.is_free
        ))

    total_pages = (total + page_size - 1) // page_size

    return CourseList(
        courses=courses_data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
        course_id: int,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    """Получение детальной информации о курсе"""

    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Проверка доступа к неопубликованным курсам
    if not course.is_published:
        if not current_user or (
                current_user.id != course.instructor_id and
                current_user.role != UserRole.ADMIN
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    return build_course_response(course, db)


@router.get("/slug/{slug}", response_model=CourseResponse)
async def get_course_by_slug(
        slug: str,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    """Получение курса по slug"""

    course = db.query(Course).filter(Course.slug == slug).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Проверка доступа
    if not course.is_published:
        if not current_user or (
                current_user.id != course.instructor_id and
                current_user.role != UserRole.ADMIN
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    return build_course_response(course, db)


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
        course_id: int,
        course_data: CourseUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Обновление курса"""

    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Проверка прав доступа
    if course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this course"
        )

    # Обновление полей
    update_data = course_data.model_dump(exclude_unset=True)

    # Обновление slug если изменился title
    if "title" in update_data:
        new_slug = generate_slug(update_data["title"])
        if new_slug != course.slug:
            # Проверка уникальности
            counter = 1
            slug = new_slug
            while db.query(Course).filter(
                    Course.slug == slug,
                    Course.id != course_id
            ).first():
                slug = f"{new_slug}-{counter}"
                counter += 1
            update_data["slug"] = slug

    for field, value in update_data.items():
        setattr(course, field, value)

    course.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(course)

    return build_course_response(course, db)


@router.patch("/{course_id}/publish", response_model=CourseResponse)
async def publish_course(
        course_id: int,
        publish_data: CoursePublish,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Публикация/снятие с публикации курса"""

    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Проверка прав
    if course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish this course"
        )

    course.is_published = publish_data.is_published

    if publish_data.is_published:
        course.status = CourseStatus.PUBLISHED
        if not course.published_at:
            course.published_at = datetime.utcnow()
    else:
        course.status = CourseStatus.DRAFT

    db.commit()
    db.refresh(course)

    return build_course_response(course, db)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
        course_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Удаление курса"""

    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Только автор или админ могут удалить
    if course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this course"
        )

    # Проверка, есть ли студенты на курсе
    enrollments_count = db.query(Enrollment).filter(
        Enrollment.course_id == course_id
    ).count()

    if enrollments_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete course with enrolled students. Archive it instead."
        )

    db.delete(course)
    db.commit()

    return None


@router.get("/my/instructor", response_model=CourseList)
async def get_my_courses(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        current_user: User = Depends(require_role([UserRole.INSTRUCTOR, UserRole.ADMIN])),
        db: Session = Depends(get_db)
):
    """Получение курсов текущего преподавателя"""

    query = db.query(Course).filter(Course.instructor_id == current_user.id)

    total = query.count()
    offset = (page - 1) * page_size
    courses = query.order_by(Course.created_at.desc()).offset(offset).limit(page_size).all()

    courses_data = []
    for course in courses:
        instructor_name = f"{course.instructor.first_name} {course.instructor.last_name}"
        category_name = course.category.name if course.category else None

        courses_data.append(CourseShort(
            id=course.id,
            title=course.title,
            short_description=course.short_description,
            thumbnail_url=course.thumbnail_url,
            level=course.level,
            price=course.price,
            discount_price=course.discount_price,
            average_rating=course.average_rating,
            total_students=course.total_students,
            total_lessons=course.total_lessons,
            duration_hours=course.duration_hours,
            instructor_name=instructor_name,
            category_name=category_name,
            is_free=course.is_free
        ))

    total_pages = (total + page_size - 1) // page_size

    return CourseList(
        courses=courses_data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )