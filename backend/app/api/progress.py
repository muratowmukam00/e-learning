from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Progress, Enrollment, Lesson, Course, EnrollmentStatus
from app.schemas.progress import (
    ProgressCreate,
    ProgressUpdate,
    ProgressResponse,
    LessonProgressResponse,
    CourseProgressSummary,
    StudentStatistics
)
from app.utils.dependencies import get_current_user
from app.models.user import User

# Создаем роутер
router = APIRouter(prefix="/progress", tags=["Progress"])


@router.post("/lessons/{lesson_id}/start", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED)
def start_lesson(
        lesson_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Начать урок (создать запись прогресса)

    - **lesson_id**: ID урока
    - Проверяет запись на курс
    - Создает запись прогресса или обновляет last_accessed_at
    """
    # Проверяем существование урока
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Проверяем, записан ли студент на курс
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == lesson.course_id,
        Enrollment.status == EnrollmentStatus.ACTIVE
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=403,
            detail="Вы не записаны на этот курс"
        )

    # Проверяем, есть ли уже запись прогресса
    existing_progress = db.query(Progress).filter(
        Progress.student_id == current_user.id,
        Progress.lesson_id == lesson_id
    ).first()

    if existing_progress:
        # Обновляем last_accessed_at
        existing_progress.last_accessed_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_progress)
        return existing_progress

    # Создаем новую запись прогресса
    progress = Progress(
        student_id=current_user.id,
        lesson_id=lesson_id,
        is_completed=False,
        completion_percentage=0.0,
        time_spent=0
    )

    db.add(progress)
    db.commit()
    db.refresh(progress)

    return progress


@router.patch("/lessons/{lesson_id}", response_model=ProgressResponse)
def update_lesson_progress(
        lesson_id: int,
        progress_data: ProgressUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Обновить прогресс по уроку

    - **lesson_id**: ID урока
    - **is_completed**: Завершен ли урок
    - **completion_percentage**: Процент просмотра (0-100)
    - **time_spent**: Время в секундах
    """
    # Получаем запись прогресса
    progress = db.query(Progress).filter(
        Progress.student_id == current_user.id,
        Progress.lesson_id == lesson_id
    ).first()

    if not progress:
        raise HTTPException(
            status_code=404,
            detail="Запись прогресса не найдена. Сначала начните урок."
        )

    # Обновляем поля
    if progress_data.is_completed is not None:
        progress.is_completed = progress_data.is_completed
        if progress_data.is_completed and not progress.completed_at:
            progress.completed_at = datetime.utcnow()

    if progress_data.completion_percentage is not None:
        progress.completion_percentage = progress_data.completion_percentage

    if progress_data.time_spent is not None:
        progress.time_spent = progress_data.time_spent

    progress.last_accessed_at = datetime.utcnow()

    db.commit()
    db.refresh(progress)

    # Обновляем прогресс в enrollment
    _update_enrollment_progress(db, current_user.id, lesson_id)

    return progress


@router.post("/lessons/{lesson_id}/complete", response_model=ProgressResponse)
def complete_lesson(
        lesson_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Отметить урок как завершенный

    - **lesson_id**: ID урока
    - Автоматически устанавливает completion_percentage = 100%
    - Обновляет прогресс курса
    """
    progress = db.query(Progress).filter(
        Progress.student_id == current_user.id,
        Progress.lesson_id == lesson_id
    ).first()

    if not progress:
        raise HTTPException(
            status_code=404,
            detail="Запись прогресса не найдена. Сначала начните урок."
        )

    progress.is_completed = True
    progress.completion_percentage = 100.0
    progress.completed_at = datetime.utcnow()
    progress.last_accessed_at = datetime.utcnow()

    db.commit()
    db.refresh(progress)

    # Обновляем прогресс в enrollment
    _update_enrollment_progress(db, current_user.id, lesson_id)

    return progress


@router.get("/courses/{course_id}", response_model=List[LessonProgressResponse])
def get_course_progress(
        course_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить прогресс по всем урокам курса

    - **course_id**: ID курса
    - Возвращает список всех уроков с прогрессом
    """
    # Проверяем запись на курс
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=403,
            detail="Вы не записаны на этот курс"
        )

    # Получаем все уроки курса с прогрессом
    lessons = db.query(Lesson).filter(
        Lesson.course_id == course_id,
        Lesson.is_published == True
    ).order_by(Lesson.order).all()

    result = []
    for lesson in lessons:
        progress = db.query(Progress).filter(
            Progress.student_id == current_user.id,
            Progress.lesson_id == lesson.id
        ).first()

        result.append(LessonProgressResponse(
            lesson_id=lesson.id,
            lesson_title=lesson.title,
            lesson_order=lesson.order,
            is_completed=progress.is_completed if progress else False,
            completion_percentage=progress.completion_percentage if progress else 0.0,
            time_spent=progress.time_spent if progress else 0,
            last_accessed_at=progress.last_accessed_at if progress else lesson.created_at
        ))

    return result


@router.get("/my-courses", response_model=List[CourseProgressSummary])
def get_my_courses_progress(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить прогресс по всем курсам текущего студента

    - Возвращает сводку по каждому курсу
    - Включает статистику: уроки, прогресс, время
    """
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id
    ).all()

    result = []
    for enrollment in enrollments:
        course = enrollment.course

        # Считаем статистику
        total_lessons = db.query(Lesson).filter(
            Lesson.course_id == course.id,
            Lesson.is_published == True
        ).count()

        completed_lessons = db.query(Progress).join(Lesson).filter(
            Progress.student_id == current_user.id,
            Lesson.course_id == course.id,
            Progress.is_completed == True
        ).count()

        total_time = db.query(func.sum(Progress.time_spent)).join(Lesson).filter(
            Progress.student_id == current_user.id,
            Lesson.course_id == course.id
        ).scalar() or 0

        progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

        result.append(CourseProgressSummary(
            course_id=course.id,
            course_title=course.title,
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            progress_percentage=round(progress_percentage, 2),
            total_time_spent=total_time,
            enrolled_at=enrollment.enrolled_at,
            last_accessed_at=enrollment.last_accessed_at
        ))

    return result


@router.get("/statistics", response_model=StudentStatistics)
def get_my_statistics(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить общую статистику студента

    - Общее количество курсов
    - Завершенные курсы
    - Курсы в процессе
    - Завершенные уроки
    - Общее время обучения
    - Средний прогресс
    """
    # Общее количество курсов
    total_enrolled = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id
    ).count()

    # Завершенные курсы
    completed_courses = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.status == EnrollmentStatus.COMPLETED
    ).count()

    # Курсы в процессе
    in_progress = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.status == EnrollmentStatus.ACTIVE
    ).count()

    # Общее количество завершенных уроков
    total_lessons_completed = db.query(Progress).filter(
        Progress.student_id == current_user.id,
        Progress.is_completed == True
    ).count()

    # Общее время обучения
    total_time = db.query(func.sum(Progress.time_spent)).filter(
        Progress.student_id == current_user.id
    ).scalar() or 0

    # Средний прогресс
    avg_progress = db.query(func.avg(Enrollment.progress_percentage)).filter(
        Enrollment.student_id == current_user.id
    ).scalar() or 0.0

    return StudentStatistics(
        total_enrolled_courses=total_enrolled,
        completed_courses=completed_courses,
        in_progress_courses=in_progress,
        total_lessons_completed=total_lessons_completed,
        total_time_spent=total_time,
        average_progress=round(avg_progress, 2)
    )


def _update_enrollment_progress(db: Session, student_id: int, lesson_id: int):
    """
    Вспомогательная функция для обновления прогресса в Enrollment

    - Пересчитывает процент завершения курса
    - Обновляет количество завершенных уроков
    - Автоматически завершает курс при 100%
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        return

    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.course_id == lesson.course_id
    ).first()

    if not enrollment:
        return

    # Считаем прогресс
    total_lessons = db.query(Lesson).filter(
        Lesson.course_id == lesson.course_id,
        Lesson.is_published == True
    ).count()

    completed_lessons = db.query(Progress).join(Lesson).filter(
        Progress.student_id == student_id,
        Lesson.course_id == lesson.course_id,
        Progress.is_completed == True
    ).count()

    # Обновляем enrollment
    enrollment.completed_lessons = completed_lessons
    enrollment.progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    enrollment.last_accessed_at = datetime.utcnow()

    # Если курс завершен на 100%
    if enrollment.progress_percentage >= 100:
        enrollment.status = EnrollmentStatus.COMPLETED
        enrollment.completed_at = datetime.utcnow()

    db.commit()