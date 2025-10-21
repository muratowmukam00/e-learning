from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentDetail,
    EnrollmentWithCourse,
    StudentListResponse
)
from app.utils.dependencies import get_current_user, require_instructor, require_admin

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
        enrollment_data: EnrollmentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Записаться на курс (для студентов)
    """
    # Проверяем существование курса
    course = db.query(Course).filter(Course.id == enrollment_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )

    # Проверяем, что курс опубликован
    if not course.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Курс еще не опубликован"
        )

    # Проверяем, не записан ли уже пользователь
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == enrollment_data.course_id
    ).first()

    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже записаны на этот курс"
        )

    # Создаем запись
    enrollment = Enrollment(
        student_id=current_user.id,
        course_id=enrollment_data.course_id,
        price_paid=course.effective_price,
        is_paid=(course.price == 0.0)  # Бесплатные курсы автоматически оплачены
    )

    db.add(enrollment)

    # Увеличиваем счетчик студентов курса
    course.total_students += 1

    db.commit()
    db.refresh(enrollment)

    return enrollment


@router.get("/my-courses", response_model=List[EnrollmentWithCourse])
async def get_my_enrollments(
        status_filter: Optional[EnrollmentStatus] = Query(None, description="Фильтр по статусу"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить список курсов, на которые записан текущий пользователь
    """
    query = db.query(Enrollment).filter(Enrollment.student_id == current_user.id)

    if status_filter:
        query = query.filter(Enrollment.status == status_filter)

    enrollments = query.order_by(Enrollment.enrolled_at.desc()).all()

    # Добавляем информацию о курсе
    result = []
    for enrollment in enrollments:
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        result.append({
            **enrollment.__dict__,
            "course": course
        })

    return result


@router.get("/{enrollment_id}", response_model=EnrollmentDetail)
async def get_enrollment(
        enrollment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о конкретной записи
    """
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена"
        )

    # Проверка доступа
    if enrollment.student_id != current_user.id and current_user.role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этой записи"
        )

    return enrollment


@router.get("/course/{course_id}/students", response_model=List[StudentListResponse])
async def get_course_students(
        course_id: int,
        status_filter: Optional[EnrollmentStatus] = Query(None),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(require_instructor)
):
    """
    Получить список студентов курса (только для преподавателей/админов)
    """
    # Проверяем курс
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )

    # Проверяем права доступа
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на просмотр студентов этого курса"
        )

    # Получаем студентов
    query = db.query(Enrollment).filter(Enrollment.course_id == course_id)

    if status_filter:
        query = query.filter(Enrollment.status == status_filter)

    enrollments = query.order_by(Enrollment.enrolled_at.desc()).offset(skip).limit(limit).all()

    # Добавляем информацию о студентах
    result = []
    for enrollment in enrollments:
        student = db.query(User).filter(User.id == enrollment.student_id).first()
        result.append({
            "enrollment_id": enrollment.id,
            "student_id": student.id,
            "student_name": student.full_name,
            "student_email": student.email,
            "student_avatar": student.avatar_url,
            "progress_percentage": enrollment.progress_percentage,
            "completed_lessons": enrollment.completed_lessons,
            "status": enrollment.status,
            "enrolled_at": enrollment.enrolled_at,
            "last_accessed_at": enrollment.last_accessed_at
        })

    return result


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_enrollment(
        enrollment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Отменить запись на курс
    """
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена"
        )

    # Проверка прав
    if enrollment.student_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на отмену этой записи"
        )

    # Обновляем статус вместо удаления
    enrollment.status = EnrollmentStatus.DROPPED

    # Уменьшаем счетчик студентов
    course = db.query(Course).filter(Course.id == enrollment.course_id).first()
    if course:
        course.total_students = max(0, course.total_students - 1)

    db.commit()

    return None


@router.post("/{enrollment_id}/complete")
async def complete_course(
        enrollment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Отметить курс как завершенный (автоматически при 100% прогрессе)
    """
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена"
        )

    if enrollment.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на изменение этой записи"
        )

    # Проверяем прогресс
    if enrollment.progress_percentage < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Курс не завершен. Прогресс: {enrollment.progress_percentage}%"
        )

    enrollment.status = EnrollmentStatus.COMPLETED
    enrollment.completed_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Курс успешно завершен!",
        "completed_at": enrollment.completed_at
    }


@router.get("/check/{course_id}")
async def check_enrollment(
        course_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Проверить, записан ли пользователь на курс
    """
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()

    if not enrollment:
        return {
            "is_enrolled": False,
            "has_access": False
        }

    return {
        "is_enrolled": True,
        "has_access": enrollment.status == EnrollmentStatus.ACTIVE,
        "progress_percentage": enrollment.progress_percentage,
        "status": enrollment.status
    }


@router.get("/course/{course_id}/statistics")
async def get_course_statistics(
        course_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_instructor)
):
    """
    Получить статистику курса (только для преподавателей/админов)
    """
    # Проверяем курс
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )

    # Проверяем права
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на просмотр статистики этого курса"
        )

    # Собираем статистику
    total_enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).count()

    active_students = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.status == EnrollmentStatus.ACTIVE
    ).count()

    completed_students = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.status == EnrollmentStatus.COMPLETED
    ).count()

    # Средний прогресс
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    avg_progress = sum(e.progress_percentage for e in enrollments) / len(enrollments) if enrollments else 0

    return {
        "course_id": course_id,
        "course_title": course.title,
        "total_enrollments": total_enrollments,
        "active_students": active_students,
        "completed_students": completed_students,
        "dropped_students": total_enrollments - active_students - completed_students,
        "average_progress": round(avg_progress, 2),
        "completion_rate": round((completed_students / total_enrollments * 100), 2) if total_enrollments > 0 else 0
    }