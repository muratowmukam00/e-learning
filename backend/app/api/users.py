from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import User, Course, Enrollment, Progress, EnrollmentStatus, Review
from app.models.user import UserRole
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UserPasswordChange,
    UserShort,
    UserList
)
from app.utils.dependencies import get_current_user
from app.utils.security import verify_password, get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch("/me", response_model=UserResponse)
def update_my_profile(
        user_data: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Обновить профиль текущего пользователя

    - **first_name**: Имя
    - **last_name**: Фамилия
    - **phone**: Телефон
    - **bio**: Биография
    - **avatar_url**: URL аватара
    """
    # Обновляем только переданные поля
    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.patch("/me/password", status_code=status.HTTP_200_OK)
def change_password(
        password_data: UserPasswordChange,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Изменить пароль текущего пользователя

    - **old_password**: Старый пароль
    - **new_password**: Новый пароль (минимум 6 символов)
    """
    # Проверяем старый пароль
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный старый пароль"
        )

    # Проверяем, что новый пароль отличается от старого
    if password_data.old_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новый пароль должен отличаться от старого"
        )

    # Обновляем пароль
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Пароль успешно изменён"}


@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(
        user_id: int,
        db: Session = Depends(get_db)
):
    """
    Получить публичный профиль пользователя

    - **user_id**: ID пользователя

    Возвращает публичную информацию о пользователе
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    return user


@router.get("/me/dashboard")
def get_my_dashboard(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить дашборд текущего пользователя

    Возвращает разную информацию в зависимости от роли:
    - **Student**: курсы, прогресс, статистика
    - **Instructor**: созданные курсы, студенты, статистика
    - **Admin**: общая статистика платформы
    """
    if current_user.role == UserRole.STUDENT:
        return _get_student_dashboard(db, current_user)
    elif current_user.role == UserRole.INSTRUCTOR:
        return _get_instructor_dashboard(db, current_user)
    elif current_user.role == UserRole.ADMIN:
        return _get_admin_dashboard(db, current_user)


def _get_student_dashboard(db: Session, user: User):
    """Дашборд для студента"""

    # Количество записей на курсы
    total_enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == user.id
    ).count()

    # Активные курсы
    active_courses = db.query(Enrollment).filter(
        Enrollment.student_id == user.id,
        Enrollment.status == EnrollmentStatus.ACTIVE
    ).count()

    # Завершённые курсы
    completed_courses = db.query(Enrollment).filter(
        Enrollment.student_id == user.id,
        Enrollment.status == EnrollmentStatus.COMPLETED
    ).count()

    # Завершённые уроки
    completed_lessons = db.query(Progress).filter(
        Progress.student_id == user.id,
        Progress.is_completed == True
    ).count()

    # Общее время обучения
    total_time = db.query(func.sum(Progress.time_spent)).filter(
        Progress.student_id == user.id
    ).scalar() or 0

    # Средний прогресс
    avg_progress = db.query(func.avg(Enrollment.progress_percentage)).filter(
        Enrollment.student_id == user.id
    ).scalar() or 0.0

    # Последние активные курсы
    recent_courses = db.query(Enrollment).filter(
        Enrollment.student_id == user.id,
        Enrollment.status == EnrollmentStatus.ACTIVE
    ).order_by(Enrollment.last_accessed_at.desc()).limit(5).all()

    recent_courses_data = []
    for enrollment in recent_courses:
        course = enrollment.course
        recent_courses_data.append({
            "course_id": course.id,
            "course_title": course.title,
            "course_thumbnail": course.thumbnail_url,
            "progress_percentage": enrollment.progress_percentage,
            "last_accessed": enrollment.last_accessed_at
        })

    return {
        "role": "student",
        "statistics": {
            "total_enrollments": total_enrollments,
            "active_courses": active_courses,
            "completed_courses": completed_courses,
            "completed_lessons": completed_lessons,
            "total_time_spent": total_time,
            "average_progress": round(avg_progress, 2)
        },
        "recent_courses": recent_courses_data
    }


def _get_instructor_dashboard(db: Session, user: User):
    """Дашборд для преподавателя"""

    # Количество созданных курсов
    total_courses = db.query(Course).filter(
        Course.instructor_id == user.id
    ).count()

    # Опубликованные курсы
    published_courses = db.query(Course).filter(
        Course.instructor_id == user.id,
        Course.is_published == True
    ).count()

    # Общее количество студентов
    total_students = db.query(func.sum(Course.total_students)).filter(
        Course.instructor_id == user.id
    ).scalar() or 0

    # Средний рейтинг курсов
    avg_rating = db.query(func.avg(Course.average_rating)).filter(
        Course.instructor_id == user.id
    ).scalar() or 0.0

    # Общее количество отзывов
    total_reviews = db.query(func.sum(Course.total_reviews)).filter(
        Course.instructor_id == user.id
    ).scalar() or 0

    # Общее количество уроков
    total_lessons = db.query(func.sum(Course.total_lessons)).filter(
        Course.instructor_id == user.id
    ).scalar() or 0

    # Последние курсы
    recent_courses = db.query(Course).filter(
        Course.instructor_id == user.id
    ).order_by(Course.created_at.desc()).limit(5).all()

    recent_courses_data = []
    for course in recent_courses:
        recent_courses_data.append({
            "course_id": course.id,
            "course_title": course.title,
            "course_thumbnail": course.thumbnail_url,
            "total_students": course.total_students,
            "average_rating": course.average_rating,
            "is_published": course.is_published,
            "created_at": course.created_at
        })

    return {
        "role": "instructor",
        "statistics": {
            "total_courses": total_courses,
            "published_courses": published_courses,
            "total_students": total_students,
            "average_rating": round(avg_rating, 2),
            "total_reviews": total_reviews,
            "total_lessons": total_lessons
        },
        "recent_courses": recent_courses_data
    }


def _get_admin_dashboard(db: Session, user: User):
    """Дашборд для администратора"""

    # Общее количество пользователей
    total_users = db.query(User).count()

    # Студенты
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()

    # Преподаватели
    total_instructors = db.query(User).filter(User.role == UserRole.INSTRUCTOR).count()

    # Общее количество курсов
    total_courses = db.query(Course).count()

    # Опубликованные курсы
    published_courses = db.query(Course).filter(Course.is_published == True).count()

    # Общее количество записей на курсы
    total_enrollments = db.query(Enrollment).count()

    # Активные записи
    active_enrollments = db.query(Enrollment).filter(
        Enrollment.status == EnrollmentStatus.ACTIVE
    ).count()

    # Завершённые курсы
    completed_enrollments = db.query(Enrollment).filter(
        Enrollment.status == EnrollmentStatus.COMPLETED
    ).count()

    # Общее количество отзывов
    total_reviews = db.query(Review).count()

    # Средний рейтинг по платформе
    avg_rating = db.query(func.avg(Course.average_rating)).scalar() or 0.0

    return {
        "role": "admin",
        "statistics": {
            "total_users": total_users,
            "total_students": total_students,
            "total_instructors": total_instructors,
            "total_courses": total_courses,
            "published_courses": published_courses,
            "total_enrollments": total_enrollments,
            "active_enrollments": active_enrollments,
            "completed_enrollments": completed_enrollments,
            "total_reviews": total_reviews,
            "platform_average_rating": round(avg_rating, 2)
        }
    }


@router.get("/instructors", response_model=List[UserShort])
def get_instructors(
        skip: int = 0,
        limit: int = 20,
        db: Session = Depends(get_db)
):
    """
    Получить список преподавателей

    - **skip**: Сколько пропустить
    - **limit**: Лимит результатов
    """
    instructors = db.query(User).filter(
        User.role == UserRole.INSTRUCTOR,
        User.is_active == True
    ).offset(skip).limit(limit).all()

    return instructors


@router.get("/{user_id}/courses")
def get_user_courses(
        user_id: int,
        db: Session = Depends(get_db)
):
    """
    Получить курсы пользователя

    - Для студента: список записанных курсов
    - Для преподавателя: список созданных курсов
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    if user.role == UserRole.STUDENT:
        # Получаем записи студента
        enrollments = db.query(Enrollment).filter(
            Enrollment.student_id == user_id
        ).all()

        courses_data = []
        for enrollment in enrollments:
            course = enrollment.course
            courses_data.append({
                "course_id": course.id,
                "course_title": course.title,
                "course_thumbnail": course.thumbnail_url,
                "progress_percentage": enrollment.progress_percentage,
                "status": enrollment.status,
                "enrolled_at": enrollment.enrolled_at
            })

        return {
            "user_id": user_id,
            "role": "student",
            "courses": courses_data,
            "total": len(courses_data)
        }

    elif user.role == UserRole.INSTRUCTOR:
        # Получаем курсы преподавателя
        courses = db.query(Course).filter(
            Course.instructor_id == user_id
        ).all()

        courses_data = []
        for course in courses:
            courses_data.append({
                "course_id": course.id,
                "course_title": course.title,
                "course_thumbnail": course.thumbnail_url,
                "total_students": course.total_students,
                "average_rating": course.average_rating,
                "is_published": course.is_published,
                "created_at": course.created_at
            })

        return {
            "user_id": user_id,
            "role": "instructor",
            "courses": courses_data,
            "total": len(courses_data)
        }

    return {
        "user_id": user_id,
        "role": user.role,
        "courses": [],
        "total": 0
    }