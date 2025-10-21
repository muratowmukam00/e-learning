from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.models.review import Review
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewWithUser,
    ReviewStats
)
from app.utils.dependencies import get_current_user, require_instructor, require_admin

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
        review_data: ReviewCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Создать отзыв о курсе (только для студентов, прошедших курс)
    """
    # Проверяем существование курса
    course = db.query(Course).filter(Course.id == review_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )

    # Проверяем, что пользователь записан на курс
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == review_data.course_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы должны быть записаны на курс, чтобы оставить отзыв"
        )

    # Проверяем, не оставлял ли уже отзыв
    existing_review = db.query(Review).filter(
        Review.student_id == current_user.id,
        Review.course_id == review_data.course_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже оставили отзыв на этот курс. Используйте PUT для обновления."
        )

    # Создаем отзыв
    review = Review(
        student_id=current_user.id,
        course_id=review_data.course_id,
        rating=review_data.rating,
        title=review_data.title,
        comment=review_data.comment
    )

    db.add(review)

    # Обновляем статистику курса
    update_course_rating(db, review_data.course_id)

    db.commit()
    db.refresh(review)

    return review


@router.get("/course/{course_id}", response_model=List[ReviewWithUser])
async def get_course_reviews(
        course_id: int,
        rating_filter: Optional[int] = Query(None, ge=1, le=5, description="Фильтр по рейтингу"),
        sort_by: str = Query("recent", description="Сортировка: recent, rating_high, rating_low"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """
    Получить все отзывы курса
    """
    # Проверяем курс
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )

    # Базовый запрос
    query = db.query(Review).filter(Review.course_id == course_id)

    # Фильтр по рейтингу
    if rating_filter:
        query = query.filter(Review.rating == rating_filter)

    # Сортировка
    if sort_by == "recent":
        query = query.order_by(desc(Review.created_at))
    elif sort_by == "rating_high":
        query = query.order_by(desc(Review.rating), desc(Review.created_at))
    elif sort_by == "rating_low":
        query = query.order_by(Review.rating, desc(Review.created_at))

    # Пагинация
    reviews = query.offset(skip).limit(limit).all()

    # Добавляем информацию о пользователях
    result = []
    for review in reviews:
        student = db.query(User).filter(User.id == review.student_id).first()
        result.append({
            **review.__dict__,
            "student_name": student.full_name,
            "student_avatar": student.avatar_url
        })

    return result


@router.get("/{review_id}", response_model=ReviewWithUser)
async def get_review(
        review_id: int,
        db: Session = Depends(get_db)
):
    """
    Получить отзыв по ID
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отзыв не найден"
        )

    student = db.query(User).filter(User.id == review.student_id).first()

    return {
        **review.__dict__,
        "student_name": student.full_name,
        "student_avatar": student.avatar_url
    }


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
        review_id: int,
        review_data: ReviewUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Обновить свой отзыв
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отзыв не найден"
        )

    # Проверка прав
    if review.student_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете редактировать только свои отзывы"
        )

    # Обновляем поля
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    # Обновляем статистику курса
    update_course_rating(db, review.course_id)

    db.commit()
    db.refresh(review)

    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
        review_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Удалить отзыв (свой или админ)
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отзыв не найден"
        )

    # Проверка прав
    if review.student_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете удалять только свои отзывы"
        )

    course_id = review.course_id
    db.delete(review)

    # Обновляем статистику курса
    update_course_rating(db, course_id)

    db.commit()

    return None


@router.get("/user/my-reviews", response_model=List[ReviewResponse])
async def get_my_reviews(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить все отзывы текущего пользователя
    """
    reviews = db.query(Review).filter(
        Review.student_id == current_user.id
    ).order_by(desc(Review.created_at)).all()

    return reviews


@router.get("/course/{course_id}/stats", response_model=ReviewStats)
async def get_course_review_stats(
        course_id: int,
        db: Session = Depends(get_db)
):
    """
    Получить статистику отзывов курса
    """
    # Проверяем курс
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )

    # Общее количество отзывов
    total_reviews = db.query(Review).filter(Review.course_id == course_id).count()

    if total_reviews == 0:
        return {
            "course_id": course_id,
            "total_reviews": 0,
            "average_rating": 0.0,
            "rating_distribution": {
                "5": 0, "4": 0, "3": 0, "2": 0, "1": 0
            }
        }

    # Средний рейтинг
    avg_rating = db.query(func.avg(Review.rating)).filter(
        Review.course_id == course_id
    ).scalar()

    # Распределение по звездам
    rating_dist = {}
    for rating in range(1, 6):
        count = db.query(Review).filter(
            Review.course_id == course_id,
            Review.rating == rating
        ).count()
        rating_dist[str(rating)] = count

    return {
        "course_id": course_id,
        "total_reviews": total_reviews,
        "average_rating": round(avg_rating, 2) if avg_rating else 0.0,
        "rating_distribution": rating_dist
    }


@router.get("/course/{course_id}/my-review")
async def get_my_course_review(
        course_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Проверить, оставил ли пользователь отзыв на курс
    """
    review = db.query(Review).filter(
        Review.student_id == current_user.id,
        Review.course_id == course_id
    ).first()

    if not review:
        return {
            "has_review": False,
            "review": None
        }

    return {
        "has_review": True,
        "review": review
    }


def update_course_rating(db: Session, course_id: int):
    """
    Обновить средний рейтинг и количество отзывов курса
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return

    # Подсчитываем средний рейтинг
    avg_rating = db.query(func.avg(Review.rating)).filter(
        Review.course_id == course_id
    ).scalar()

    # Подсчитываем количество отзывов
    total_reviews = db.query(Review).filter(
        Review.course_id == course_id
    ).count()

    course.average_rating = round(avg_rating, 2) if avg_rating else 0.0
    course.total_reviews = total_reviews

    # Не вызываем commit здесь, это делается в основной функции