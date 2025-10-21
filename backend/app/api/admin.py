from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import (
    User, Course, Enrollment, Progress, Review,
    Comment, Quiz, QuizAttempt, Category
)
from app.models.user import UserRole
from app.models.course import CourseStatus
from app.models.enrollment import EnrollmentStatus
from app.schemas.user import UserResponse, UserList, UserShort
from app.schemas.course import CourseResponse, CourseShort
from app.utils.dependencies import get_current_user, require_role

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============ USERS MANAGEMENT ============

@router.get("/users", response_model=UserList)
def get_all_users(
        search: Optional[str] = Query(None, description="Поиск по email, имени"),
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Получить список всех пользователей (только для админа)

    - **search**: Поиск по email, имени, фамилии
    - **role**: Фильтр по роли
    - **is_active**: Фильтр по активности
    - **is_verified**: Фильтр по верификации
    """
    query = db.query(User)

    # Поиск
    if search:
        search_filter = (
                User.email.ilike(f"%{search}%") |
                User.first_name.ilike(f"%{search}%") |
                User.last_name.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    # Фильтры
    if role:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)

    # Подсчёт
    total = query.count()

    # Пагинация
    offset = (page - 1) * page_size
    users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()

    users_data = [UserShort.model_validate(user) for user in users]

    return UserList(
        users=users_data,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_details(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Получить детальную информацию о пользователе"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    return user


@router.patch("/users/{user_id}/role")
def change_user_role(
        user_id: int,
        new_role: UserRole,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Изменить роль пользователя

    - **new_role**: student, instructor, admin
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Нельзя изменить роль самому себе
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя изменить свою собственную роль"
        )

    old_role = user.role
    user.role = new_role
    db.commit()

    return {
        "message": f"Роль пользователя изменена с {old_role} на {new_role}",
        "user_id": user_id,
        "old_role": old_role,
        "new_role": new_role
    }


@router.patch("/users/{user_id}/status")
def change_user_status(
        user_id: int,
        is_active: bool,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Активировать/деактивировать пользователя

    - **is_active**: true/false
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Нельзя деактивировать самого себя
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя деактивировать свой собственный аккаунт"
        )

    user.is_active = is_active
    db.commit()

    status_text = "активирован" if is_active else "деактивирован"

    return {
        "message": f"Пользователь {status_text}",
        "user_id": user_id,
        "is_active": is_active
    }


@router.patch("/users/{user_id}/verify")
def verify_user(
        user_id: int,
        is_verified: bool,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Верифицировать/снять верификацию пользователя

    - **is_verified**: true/false
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    user.is_verified = is_verified
    db.commit()

    status_text = "верифицирован" if is_verified else "верификация снята"

    return {
        "message": f"Пользователь {status_text}",
        "user_id": user_id,
        "is_verified": is_verified
    }


@router.delete("/users/{user_id}")
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Удалить пользователя (осторожно!)

    Удаляет пользователя и все связанные данные
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Нельзя удалить самого себя
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить свой собственный аккаунт"
        )

    # Проверяем есть ли курсы у преподавателя
    if user.role == UserRole.INSTRUCTOR:
        courses_count = db.query(Course).filter(Course.instructor_id == user_id).count()
        if courses_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Невозможно удалить преподавателя с {courses_count} курсами. Сначала удалите или переназначьте курсы."
            )

    db.delete(user)
    db.commit()

    return {
        "message": "Пользователь успешно удалён",
        "user_id": user_id
    }


# ============ COURSES MANAGEMENT ============

@router.get("/courses")
def get_all_courses(
        search: Optional[str] = None,
        status: Optional[CourseStatus] = None,
        category_id: Optional[int] = None,
        instructor_id: Optional[int] = None,
        is_published: Optional[bool] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Получить все курсы включая черновики (только админ)

    - **search**: Поиск по названию
    - **status**: draft, published, archived
    - **is_published**: true/false
    """
    query = db.query(Course)

    # Поиск
    if search:
        query = query.filter(Course.title.ilike(f"%{search}%"))

    # Фильтры
    if status:
        query = query.filter(Course.status == status)

    if category_id:
        query = query.filter(Course.category_id == category_id)

    if instructor_id:
        query = query.filter(Course.instructor_id == instructor_id)

    if is_published is not None:
        query = query.filter(Course.is_published == is_published)

    # Подсчёт
    total = query.count()

    # Пагинация
    offset = (page - 1) * page_size
    courses = query.order_by(Course.created_at.desc()).offset(offset).limit(page_size).all()

    courses_data = []
    for course in courses:
        instructor_name = f"{course.instructor.first_name} {course.instructor.last_name}"
        category_name = course.category.name if course.category else None

        courses_data.append({
            "id": course.id,
            "title": course.title,
            "slug": course.slug,
            "status": course.status,
            "is_published": course.is_published,
            "instructor_id": course.instructor_id,
            "instructor_name": instructor_name,
            "category_name": category_name,
            "total_students": course.total_students,
            "average_rating": course.average_rating,
            "created_at": course.created_at,
            "published_at": course.published_at
        })

    total_pages = (total + page_size - 1) // page_size

    return {
        "courses": courses_data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.patch("/courses/{course_id}/moderate")
def moderate_course(
        course_id: int,
        action: str = Query(..., description="approve, reject, archive"),
        reason: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Модерация курса

    - **action**: approve (одобрить), reject (отклонить), archive (архивировать)
    - **reason**: Причина отклонения (опционально)
    """
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )

    if action == "approve":
        course.status = CourseStatus.PUBLISHED
        course.is_published = True
        if not course.published_at:
            course.published_at = datetime.utcnow()
        message = "Курс одобрен и опубликован"

    elif action == "reject":
        course.status = CourseStatus.DRAFT
        course.is_published = False
        message = f"Курс отклонён. Причина: {reason}" if reason else "Курс отклонён"

    elif action == "archive":
        course.status = CourseStatus.ARCHIVED
        course.is_published = False
        message = "Курс архивирован"

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверное действие. Используйте: approve, reject, archive"
        )

    db.commit()

    return {
        "message": message,
        "course_id": course_id,
        "new_status": course.status,
        "is_published": course.is_published
    }


# ============ STATISTICS ============

@router.get("/statistics")
def get_platform_statistics(
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Получить детальную статистику платформы

    Включает информацию о:
    - Пользователях
    - Курсах
    - Записях
    - Активности
    - Доходах (если есть платные курсы)
    """
    # Пользователи
    total_users = db.query(User).count()
    students_count = db.query(User).filter(User.role == UserRole.STUDENT).count()
    instructors_count = db.query(User).filter(User.role == UserRole.INSTRUCTOR).count()
    admins_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()

    # Новые пользователи за последние 30 дней
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users_30d = db.query(User).filter(User.created_at >= thirty_days_ago).count()

    # Курсы
    total_courses = db.query(Course).count()
    published_courses = db.query(Course).filter(Course.is_published == True).count()
    draft_courses = db.query(Course).filter(Course.status == CourseStatus.DRAFT).count()
    archived_courses = db.query(Course).filter(Course.status == CourseStatus.ARCHIVED).count()

    # Новые курсы за 30 дней
    new_courses_30d = db.query(Course).filter(Course.created_at >= thirty_days_ago).count()

    # Записи на курсы
    total_enrollments = db.query(Enrollment).count()
    active_enrollments = db.query(Enrollment).filter(
        Enrollment.status == EnrollmentStatus.ACTIVE
    ).count()
    completed_enrollments = db.query(Enrollment).filter(
        Enrollment.status == EnrollmentStatus.COMPLETED
    ).count()

    # Новые записи за 30 дней
    new_enrollments_30d = db.query(Enrollment).filter(
        Enrollment.enrolled_at >= thirty_days_ago
    ).count()

    # Средний процент завершения
    avg_completion = db.query(func.avg(Enrollment.progress_percentage)).scalar() or 0.0

    # Уроки
    total_lessons = db.query(func.sum(Course.total_lessons)).scalar() or 0

    # Завершённые уроки
    completed_lessons = db.query(Progress).filter(Progress.is_completed == True).count()

    # Отзывы
    total_reviews = db.query(Review).count()
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 0.0

    # Комментарии
    total_comments = db.query(Comment).filter(Comment.is_deleted == False).count()

    # Квизы
    total_quizzes = db.query(Quiz).count()
    total_quiz_attempts = db.query(QuizAttempt).count()
    passed_attempts = db.query(QuizAttempt).filter(QuizAttempt.is_passed == True).count()
    quiz_pass_rate = (passed_attempts / total_quiz_attempts * 100) if total_quiz_attempts > 0 else 0

    # Категории
    total_categories = db.query(Category).count()

    # Топ-5 курсов по студентам
    top_courses = db.query(Course).order_by(
        Course.total_students.desc()
    ).limit(5).all()

    top_courses_data = [
        {
            "id": c.id,
            "title": c.title,
            "total_students": c.total_students,
            "average_rating": c.average_rating
        }
        for c in top_courses
    ]

    # Топ-5 преподавателей
    top_instructors = db.query(
        User.id,
        User.first_name,
        User.last_name,
        func.count(Course.id).label("courses_count"),
        func.sum(Course.total_students).label("total_students")
    ).join(Course, Course.instructor_id == User.id).group_by(
        User.id
    ).order_by(desc("total_students")).limit(5).all()

    top_instructors_data = [
        {
            "id": i.id,
            "name": f"{i.first_name} {i.last_name}",
            "courses_count": i.courses_count,
            "total_students": i.total_students or 0
        }
        for i in top_instructors
    ]

    return {
        "users": {
            "total": total_users,
            "students": students_count,
            "instructors": instructors_count,
            "admins": admins_count,
            "active": active_users,
            "verified": verified_users,
            "new_last_30_days": new_users_30d
        },
        "courses": {
            "total": total_courses,
            "published": published_courses,
            "draft": draft_courses,
            "archived": archived_courses,
            "new_last_30_days": new_courses_30d
        },
        "enrollments": {
            "total": total_enrollments,
            "active": active_enrollments,
            "completed": completed_enrollments,
            "new_last_30_days": new_enrollments_30d,
            "average_completion_percentage": round(avg_completion, 2)
        },
        "content": {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "total_reviews": total_reviews,
            "average_rating": round(avg_rating, 2),
            "total_comments": total_comments,
            "total_categories": total_categories
        },
        "quizzes": {
            "total": total_quizzes,
            "total_attempts": total_quiz_attempts,
            "passed_attempts": passed_attempts,
            "pass_rate": round(quiz_pass_rate, 2)
        },
        "top_courses": top_courses_data,
        "top_instructors": top_instructors_data
    }


@router.get("/recent-activity")
def get_recent_activity(
        limit: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Получить последнюю активность на платформе

    - Новые пользователи
    - Новые курсы
    - Новые записи
    - Новые отзывы
    """
    # Новые пользователи
    recent_users = db.query(User).order_by(
        User.created_at.desc()
    ).limit(limit).all()

    # Новые курсы
    recent_courses = db.query(Course).order_by(
        Course.created_at.desc()
    ).limit(limit).all()

    # Новые записи
    recent_enrollments = db.query(Enrollment).order_by(
        Enrollment.enrolled_at.desc()
    ).limit(limit).all()

    # Новые отзывы
    recent_reviews = db.query(Review).order_by(
        Review.created_at.desc()
    ).limit(limit).all()

    return {
        "recent_users": [
            {
                "id": u.id,
                "email": u.email,
                "name": f"{u.first_name} {u.last_name}",
                "role": u.role,
                "created_at": u.created_at
            }
            for u in recent_users
        ],
        "recent_courses": [
            {
                "id": c.id,
                "title": c.title,
                "instructor": f"{c.instructor.first_name} {c.instructor.last_name}",
                "status": c.status,
                "created_at": c.created_at
            }
            for c in recent_courses
        ],
        "recent_enrollments": [
            {
                "id": e.id,
                "student": f"{e.student.first_name} {e.student.last_name}",
                "course": e.course.title,
                "enrolled_at": e.enrolled_at
            }
            for e in recent_enrollments
        ],
        "recent_reviews": [
            {
                "id": r.id,
                "student": f"{r.student.first_name} {r.student.last_name}",
                "course": r.course.title,
                "rating": r.rating,
                "created_at": r.created_at
            }
            for r in recent_reviews
        ]
    }