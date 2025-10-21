from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Comment, Lesson, Enrollment, User, EnrollmentStatus
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentWithReplies,
    LessonCommentsResponse,
    UserBrief
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
        comment_data: CommentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Создать комментарий к уроку

    - **lesson_id**: ID урока
    - **content**: Текст комментария (1-2000 символов)
    - **parent_id**: ID родительского комментария (для ответов)
    """
    # Проверяем существование урока
    lesson = db.query(Lesson).filter(Lesson.id == comment_data.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Проверяем, записан ли пользователь на курс
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == lesson.course_id,
        Enrollment.status == EnrollmentStatus.ACTIVE
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=403,
            detail="Вы должны быть записаны на курс, чтобы оставлять комментарии"
        )

    # Если это ответ на комментарий, проверяем существование родительского комментария
    if comment_data.parent_id:
        parent_comment = db.query(Comment).filter(
            Comment.id == comment_data.parent_id,
            Comment.lesson_id == comment_data.lesson_id
        ).first()

        if not parent_comment:
            raise HTTPException(status_code=404, detail="Родительский комментарий не найден")

    # Создаем комментарий
    comment = Comment(
        content=comment_data.content,
        user_id=current_user.id,
        lesson_id=comment_data.lesson_id,
        parent_id=comment_data.parent_id
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Формируем ответ
    response = CommentResponse(
        id=comment.id,
        content=comment.content,
        user_id=comment.user_id,
        lesson_id=comment.lesson_id,
        parent_id=comment.parent_id,
        is_edited=comment.is_edited,
        is_deleted=comment.is_deleted,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        user=UserBrief(
            id=current_user.id,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            avatar_url=current_user.avatar_url,
            role=current_user.role.value
        ),
        replies_count=0
    )

    return response


@router.get("/lessons/{lesson_id}", response_model=LessonCommentsResponse)
def get_lesson_comments(
        lesson_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить все комментарии урока

    - **lesson_id**: ID урока
    - Возвращает иерархию комментариев с ответами
    """
    # Проверяем существование урока
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Проверяем доступ к уроку
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == lesson.course_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=403,
            detail="У вас нет доступа к этому уроку"
        )

    # Получаем только корневые комментарии (без parent_id)
    root_comments = db.query(Comment).options(
        joinedload(Comment.user),
        joinedload(Comment.replies).joinedload(Comment.user)
    ).filter(
        Comment.lesson_id == lesson_id,
        Comment.parent_id.is_(None),
        Comment.is_deleted == False
    ).order_by(Comment.created_at.desc()).all()

    # Общее количество комментариев (включая ответы)
    total_comments = db.query(Comment).filter(
        Comment.lesson_id == lesson_id,
        Comment.is_deleted == False
    ).count()

    # Формируем ответ
    comments_list = []
    for comment in root_comments:
        # Получаем ответы
        replies = db.query(Comment).options(
            joinedload(Comment.user)
        ).filter(
            Comment.parent_id == comment.id,
            Comment.is_deleted == False
        ).order_by(Comment.created_at.asc()).all()

        replies_data = [
            CommentResponse(
                id=reply.id,
                content=reply.content,
                user_id=reply.user_id,
                lesson_id=reply.lesson_id,
                parent_id=reply.parent_id,
                is_edited=reply.is_edited,
                is_deleted=reply.is_deleted,
                created_at=reply.created_at,
                updated_at=reply.updated_at,
                user=UserBrief(
                    id=reply.user.id,
                    first_name=reply.user.first_name,
                    last_name=reply.user.last_name,
                    avatar_url=reply.user.avatar_url,
                    role=reply.user.role.value
                ),
                replies_count=0
            )
            for reply in replies
        ]

        comment_data = CommentWithReplies(
            id=comment.id,
            content=comment.content,
            user_id=comment.user_id,
            lesson_id=comment.lesson_id,
            parent_id=comment.parent_id,
            is_edited=comment.is_edited,
            is_deleted=comment.is_deleted,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            user=UserBrief(
                id=comment.user.id,
                first_name=comment.user.first_name,
                last_name=comment.user.last_name,
                avatar_url=comment.user.avatar_url,
                role=comment.user.role.value
            ),
            replies_count=len(replies),
            replies=replies_data
        )

        comments_list.append(comment_data)

    return LessonCommentsResponse(
        lesson_id=lesson_id,
        total_comments=total_comments,
        comments=comments_list
    )


@router.patch("/{comment_id}", response_model=CommentResponse)
def update_comment(
        comment_id: int,
        comment_data: CommentUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Обновить свой комментарий

    - **comment_id**: ID комментария
    - **content**: Новый текст комментария
    """
    # Получаем комментарий
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    # Проверяем, что это комментарий текущего пользователя
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Вы можете редактировать только свои комментарии"
        )

    # Обновляем комментарий
    comment.content = comment_data.content
    comment.is_edited = True
    comment.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(comment)

    # Получаем данные пользователя
    user = db.query(User).filter(User.id == comment.user_id).first()

    return CommentResponse(
        id=comment.id,
        content=comment.content,
        user_id=comment.user_id,
        lesson_id=comment.lesson_id,
        parent_id=comment.parent_id,
        is_edited=comment.is_edited,
        is_deleted=comment.is_deleted,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        user=UserBrief(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            role=user.role.value
        ),
        replies_count=len(comment.replies) if comment.replies else 0
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Удалить свой комментарий (мягкое удаление)

    - **comment_id**: ID комментария
    - Комментарий помечается как удаленный, но остается в базе
    """
    # Получаем комментарий
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    # Проверяем права (владелец или инструктор курса)
    if comment.user_id != current_user.id:
        # Проверяем, является ли пользователь инструктором курса
        lesson = db.query(Lesson).filter(Lesson.id == comment.lesson_id).first()
        if lesson and lesson.course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Вы можете удалять только свои комментарии"
            )

    # Мягкое удаление
    comment.is_deleted = True
    comment.content = "[Комментарий удален]"
    comment.updated_at = datetime.utcnow()

    db.commit()

    return None


@router.get("/my", response_model=List[CommentResponse])
def get_my_comments(
        limit: int = 20,
        offset: int = 0,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить все мои комментарии

    - **limit**: Количество комментариев (по умолчанию 20)
    - **offset**: Смещение для пагинации
    """
    comments = db.query(Comment).options(
        joinedload(Comment.user),
        joinedload(Comment.lesson)
    ).filter(
        Comment.user_id == current_user.id,
        Comment.is_deleted == False
    ).order_by(Comment.created_at.desc()).limit(limit).offset(offset).all()

    result = []
    for comment in comments:
        result.append(CommentResponse(
            id=comment.id,
            content=comment.content,
            user_id=comment.user_id,
            lesson_id=comment.lesson_id,
            parent_id=comment.parent_id,
            is_edited=comment.is_edited,
            is_deleted=comment.is_deleted,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            user=UserBrief(
                id=current_user.id,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                avatar_url=current_user.avatar_url,
                role=current_user.role.value
            ),
            replies_count=len(comment.replies) if comment.replies else 0
        ))

    return result