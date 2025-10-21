from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.lesson import Lesson
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.schemas.lessons import LessonCreate, LessonUpdate, LessonResponse, LessonDetail
from app.utils.dependencies import get_current_user, require_instructor as check_instructor_or_admin

router = APIRouter(prefix="/lessons", tags=["Lessons"])


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
        lesson_data: LessonCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_instructor_or_admin)
):
    """
    Создать новый урок (только преподаватели и админы)
    """
    # Проверяем, существует ли курс
    course = db.query(Course).filter(Course.id == lesson_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )

    # Проверяем, что пользователь является владельцем курса или админом
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на добавление уроков к этому курсу"
        )

    # Если order не указан, ставим последним
    if lesson_data.order is None:
        max_order = db.query(Lesson).filter(Lesson.course_id == lesson_data.course_id).count()
        lesson_data.order = max_order + 1

    # Создаем урок
    lesson = Lesson(**lesson_data.model_dump())
    db.add(lesson)

    # Обновляем счетчик уроков в курсе
    course.total_lessons = db.query(Lesson).filter(Lesson.course_id == course.id).count() + 1

    db.commit()
    db.refresh(lesson)

    return lesson


@router.get("/{lesson_id}", response_model=LessonDetail)
async def get_lesson(
        lesson_id: int,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    """
    Получить информацию об уроке
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )

    # Проверяем доступ к уроку
    if not lesson.is_free_preview:
        # Проверяем, записан ли пользователь на курс
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == lesson.course_id
        ).first()

        # Если не записан и не инструктор/админ - запрещаем доступ
        if not enrollment and current_user.role not in ["admin", "instructor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет доступа к этому уроку. Запишитесь на курс."
            )

    return lesson


@router.get("/course/{course_id}", response_model=List[LessonResponse])
async def get_course_lessons(
        course_id: int,
        db: Session = Depends(get_db)
):
    """
    Получить все уроки курса (в порядке следования)
    """
    # Проверяем существование курса
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )

    # Получаем все уроки курса, отсортированные по order
    lessons = db.query(Lesson).filter(
        Lesson.course_id == course_id,
        Lesson.is_published == True
    ).order_by(Lesson.order).all()

    return lessons


@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
        lesson_id: int,
        lesson_data: LessonUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_instructor_or_admin)
):
    """
    Обновить урок (только владелец курса или админ)
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )

    # Проверяем права доступа
    course = db.query(Course).filter(Course.id == lesson.course_id).first()
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на изменение этого урока"
        )

    # Обновляем поля
    update_data = lesson_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lesson, field, value)

    db.commit()
    db.refresh(lesson)

    return lesson


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
        lesson_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_instructor_or_admin)
):
    """
    Удалить урок (только владелец курса или админ)
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )

    # Проверяем права доступа
    course = db.query(Course).filter(Course.id == lesson.course_id).first()
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на удаление этого урока"
        )

    course_id = lesson.course_id

    db.delete(lesson)

    # Обновляем счетчик уроков
    course.total_lessons = db.query(Lesson).filter(Lesson.course_id == course_id).count()

    db.commit()

    return None


@router.post("/{lesson_id}/reorder")
async def reorder_lesson(
        lesson_id: int,
        new_order: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_instructor_or_admin)
):
    """
    Изменить порядок урока в курсе
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )

    # Проверяем права доступа
    course = db.query(Course).filter(Course.id == lesson.course_id).first()
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на изменение порядка уроков"
        )

    old_order = lesson.order

    # Если порядок не изменился
    if old_order == new_order:
        return {"message": "Порядок не изменен"}

    # Обновляем порядок других уроков
    if new_order < old_order:
        # Сдвигаем вниз уроки между new_order и old_order
        db.query(Lesson).filter(
            Lesson.course_id == lesson.course_id,
            Lesson.order >= new_order,
            Lesson.order < old_order
        ).update({Lesson.order: Lesson.order + 1})
    else:
        # Сдвигаем вверх уроки между old_order и new_order
        db.query(Lesson).filter(
            Lesson.course_id == lesson.course_id,
            Lesson.order > old_order,
            Lesson.order <= new_order
        ).update({Lesson.order: Lesson.order - 1})

    # Устанавливаем новый порядок для текущего урока
    lesson.order = new_order

    db.commit()

    return {"message": "Порядок урока успешно изменен"}


# Добавьте эти эндпоинты в конец файла app/api/lessons.py

@router.get("/course/{course_id}/preview", response_model=List[LessonResponse])
async def get_preview_lessons(
        course_id: int,
        db: Session = Depends(get_db)
):
    """
    Получить бесплатные уроки для предпросмотра курса
    (доступно без авторизации)
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )

    # Получаем только бесплатные уроки
    lessons = db.query(Lesson).filter(
        Lesson.course_id == course_id,
        Lesson.is_free_preview == True,
        Lesson.is_published == True
    ).order_by(Lesson.order).all()

    return lessons


@router.post("/{lesson_id}/complete")
async def mark_lesson_complete(
        lesson_id: int,
        completion_data: dict,  # {"completion_percentage": 100, "time_spent": 300}
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Отметить урок как просмотренный/завершенный
    """
    from app.models.progress import Progress

    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )

    # Проверяем, записан ли пользователь на курс
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == lesson.course_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не записаны на этот курс"
        )

    # Ищем или создаем запись о прогрессе
    progress = db.query(Progress).filter(
        Progress.student_id == current_user.id,
        Progress.lesson_id == lesson_id
    ).first()

    if not progress:
        progress = Progress(
            student_id=current_user.id,
            lesson_id=lesson_id
        )
        db.add(progress)

    # Обновляем прогресс
    progress.completion_percentage = completion_data.get("completion_percentage", 100)
    progress.time_spent += completion_data.get("time_spent", 0)

    if progress.completion_percentage >= 100:
        progress.is_completed = True
        if not progress.completed_at:
            progress.completed_at = datetime.utcnow()

    # Пересчитываем прогресс по курсу
    total_lessons = db.query(Lesson).filter(
        Lesson.course_id == lesson.course_id,
        Lesson.is_published == True
    ).count()

    completed_lessons = db.query(Progress).filter(
        Progress.student_id == current_user.id,
        Progress.is_completed == True,
        Progress.lesson_id.in_(
            db.query(Lesson.id).filter(Lesson.course_id == lesson.course_id)
        )
    ).count()

    # Обновляем enrollment
    enrollment.completed_lessons = completed_lessons
    if total_lessons > 0:
        enrollment.progress_percentage = (completed_lessons / total_lessons) * 100

    # Если курс завершен
    if enrollment.progress_percentage >= 100:
        enrollment.status = "completed"
        if not enrollment.completed_at:
            enrollment.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(progress)

    return {
        "message": "Прогресс обновлен",
        "lesson_progress": {
            "is_completed": progress.is_completed,
            "completion_percentage": progress.completion_percentage,
            "time_spent": progress.time_spent
        },
        "course_progress": {
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "progress_percentage": enrollment.progress_percentage
        }
    }


@router.get("/course/{course_id}/with-progress", response_model=List[dict])
async def get_lessons_with_progress(
        course_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить все уроки курса с информацией о прогрессе студента
    """
    from app.models.progress import Progress

    # Проверяем доступ к курсу
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()

    if not enrollment and current_user.role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этому курсу"
        )

    # Получаем уроки
    lessons = db.query(Lesson).filter(
        Lesson.course_id == course_id,
        Lesson.is_published == True
    ).order_by(Lesson.order).all()

    # Добавляем информацию о прогрессе
    result = []
    for lesson in lessons:
        progress = db.query(Progress).filter(
            Progress.student_id == current_user.id,
            Progress.lesson_id == lesson.id
        ).first()

        lesson_data = {
            "id": lesson.id,
            "title": lesson.title,
            "description": lesson.description,
            "lesson_type": lesson.lesson_type,
            "order": lesson.order,
            "video_duration": lesson.video_duration,
            "is_free_preview": lesson.is_free_preview,
            "progress": {
                "is_completed": progress.is_completed if progress else False,
                "completion_percentage": progress.completion_percentage if progress else 0,
                "time_spent": progress.time_spent if progress else 0,
                "last_accessed": progress.last_accessed_at if progress else None
            }
        }
        result.append(lesson_data)

    return result


@router.post("/bulk-create")
async def bulk_create_lessons(
        lessons_data: List[LessonCreate],
        db: Session = Depends(get_db),
        current_user: User = Depends(check_instructor_or_admin)
):
    """
    Массовое создание уроков (полезно для импорта)
    """
    if not lessons_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Список уроков пуст"
        )

    # Проверяем, что все уроки принадлежат одному курсу
    course_ids = set(lesson.course_id for lesson in lessons_data)
    if len(course_ids) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Все уроки должны принадлежать одному курсу"
        )

    course_id = list(course_ids)[0]

    # Проверяем курс и права
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )

    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на добавление уроков к этому курсу"
        )

    # Создаем уроки
    created_lessons = []
    for lesson_data in lessons_data:
        lesson = Lesson(**lesson_data.model_dump())
        db.add(lesson)
        created_lessons.append(lesson)

    # Обновляем счетчик уроков
    course.total_lessons = db.query(Lesson).filter(Lesson.course_id == course_id).count() + len(created_lessons)

    db.commit()

    return {
        "message": f"Создано уроков: {len(created_lessons)}",
        "lessons": [{"id": l.id, "title": l.title} for l in created_lessons]
    }