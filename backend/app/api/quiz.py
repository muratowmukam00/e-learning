from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List
from datetime import datetime
import random

from app.database import get_db
from app.models import (
    Quiz, QuizQuestion, QuizAnswer, QuizAttempt,
    Lesson, Course, Enrollment, EnrollmentStatus, User, UserRole
)
from app.schemas.quiz import (
    QuizCreate, QuizUpdate, QuizResponse, QuizResponsePublic, QuizListItem,
    QuizQuestionCreate, QuizQuestionUpdate, QuizQuestionResponse,
    QuizAttemptSubmit, QuizAttemptResult, QuizAttemptResponse,
    QuestionResult, StudentAnswer, QuizStatistics
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


# ============ CRUD ДЛЯ КВИЗОВ (Инструктор) ============

@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def create_quiz(
        quiz_data: QuizCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Создать квиз для урока (только инструктор)

    - **lesson_id**: ID урока
    - **title**: Название квиза
    - **description**: Описание
    - **passing_score**: Минимальный процент для прохождения (0-100)
    - **time_limit**: Ограничение времени в минутах
    - **max_attempts**: Максимальное количество попыток
    """
    # Проверяем урок
    lesson = db.query(Lesson).filter(Lesson.id == quiz_data.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Проверяем права (владелец курса)
    if lesson.course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Только инструктор курса может создавать квизы"
        )

    # Создаем квиз
    quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        lesson_id=quiz_data.lesson_id,
        passing_score=quiz_data.passing_score,
        time_limit=quiz_data.time_limit,
        max_attempts=quiz_data.max_attempts,
        show_correct_answers=quiz_data.show_correct_answers,
        randomize_questions=quiz_data.randomize_questions,
        randomize_answers=quiz_data.randomize_answers,
        is_published=quiz_data.is_published
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return quiz


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz_details(
        quiz_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить детали квиза (только инструктор - с правильными ответами)
    """
    quiz = db.query(Quiz).options(
        joinedload(Quiz.questions).joinedload(QuizQuestion.answers)
    ).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Квиз не найден")

    # Проверяем права
    lesson = db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()
    if lesson.course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Доступ запрещен"
        )

    return quiz


@router.patch("/{quiz_id}", response_model=QuizResponse)
def update_quiz(
        quiz_id: int,
        quiz_data: QuizUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Обновить квиз (только инструктор)
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Квиз не найден")

    # Проверяем права
    lesson = db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()
    if lesson.course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    # Обновляем поля
    update_data = quiz_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quiz, field, value)

    quiz.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(quiz)

    return quiz


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
        quiz_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Удалить квиз (только инструктор)
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Квиз не найден")

    # Проверяем права
    lesson = db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()
    if lesson.course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    db.delete(quiz)
    db.commit()

    return None


# ============ CRUD ДЛЯ ВОПРОСОВ ============

@router.post("/{quiz_id}/questions", response_model=QuizQuestionResponse, status_code=status.HTTP_201_CREATED)
def add_question(
        quiz_id: int,
        question_data: QuizQuestionCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Добавить вопрос в квиз (только инструктор)

    - **question_text**: Текст вопроса
    - **question_type**: Тип вопроса (multiple_choice, multiple_select, true_false, short_answer)
    - **points**: Баллы за вопрос
    - **answers**: Список ответов (минимум 2)
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Квиз не найден")

    # Проверяем права
    lesson = db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()
    if lesson.course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    # Проверяем наличие хотя бы одного правильного ответа
    has_correct = any(answer.is_correct for answer in question_data.answers)
    if not has_correct:
        raise HTTPException(
            status_code=400,
            detail="Должен быть хотя бы один правильный ответ"
        )

    # Создаем вопрос
    question = QuizQuestion(
        quiz_id=quiz_id,
        question_text=question_data.question_text,
        question_type=question_data.question_type,
        order=question_data.order,
        points=question_data.points,
        explanation=question_data.explanation,
        image_url=question_data.image_url
    )

    db.add(question)
    db.flush()

    # Создаем ответы
    for answer_data in question_data.answers:
        answer = QuizAnswer(
            question_id=question.id,
            answer_text=answer_data.answer_text,
            is_correct=answer_data.is_correct,
            order=answer_data.order
        )
        db.add(answer)

    db.commit()
    db.refresh(question)

    return question


@router.patch("/questions/{question_id}", response_model=QuizQuestionResponse)
def update_question(
        question_id: int,
        question_data: QuizQuestionUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Обновить вопрос (только инструктор)
    """
    question = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    # Проверяем права
    quiz = db.query(Quiz).filter(Quiz.id == question.quiz_id).first()
    lesson = db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()
    if lesson.course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    # Обновляем поля
    update_data = question_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)

    question.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(question)

    return question


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
        question_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Удалить вопрос (только инструктор)
    """
    question = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    # Проверяем права
    quiz = db.query(Quiz).filter(Quiz.id == question.quiz_id).first()
    lesson = db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()
    if lesson.course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    db.delete(question)
    db.commit()

    return None


@router.get("/lessons/{lesson_id}", response_model=List[QuizListItem])
def get_lesson_quizzes(
        lesson_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить все квизы урока
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Проверяем доступ
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == lesson.course_id
    ).first()

    is_instructor = lesson.course.instructor_id == current_user.id or current_user.role == UserRole.ADMIN

    if not enrollment and not is_instructor:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    quizzes = db.query(Quiz).filter(
        Quiz.lesson_id == lesson_id,
        Quiz.is_published == True
    ).all()

    result = []
    for quiz in quizzes:
        total_questions = db.query(QuizQuestion).filter(
            QuizQuestion.quiz_id == quiz.id
        ).count()

        result.append(QuizListItem(
            id=quiz.id,
            title=quiz.title,
            description=quiz.description,
            lesson_id=quiz.lesson_id,
            total_questions=total_questions,
            passing_score=quiz.passing_score,
            max_attempts=quiz.max_attempts,
            is_published=quiz.is_published
        ))

    return result


# ============ ПРОХОЖДЕНИЕ КВИЗОВ (Студент) ============

@router.get("/{quiz_id}/start", response_model=QuizResponsePublic)
def start_quiz(
        quiz_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Начать прохождение квиза (получить вопросы БЕЗ правильных ответов)

    - Проверяет доступ к курсу
    - Проверяет количество попыток
    - Возвращает вопросы без информации о правильных ответах
    """
    quiz = db.query(Quiz).options(
        joinedload(Quiz.questions).joinedload(QuizQuestion.answers)
    ).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Квиз не найден")

    # Проверяем доступ к курсу
    lesson = db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == lesson.course_id,
        Enrollment.status == EnrollmentStatus.ACTIVE
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=403,
            detail="Вы должны быть записаны на курс"
        )

    # Проверяем количество попыток
    attempts_count = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.completed_at.isnot(None)
    ).count()

    if attempts_count >= quiz.max_attempts:
        raise HTTPException(
            status_code=403,
            detail=f"Превышено максимальное количество попыток ({quiz.max_attempts})"
        )

    # Подготовка вопросов (без правильных ответов)
    questions = quiz.questions
    if quiz.randomize_questions:
        questions = random.sample(list(questions), len(questions))

    questions_public = []
    total_points = 0.0

    for question in questions:
        answers = question.answers
        if quiz.randomize_answers:
            answers = random.sample(list(answers), len(answers))

        # Ответы БЕЗ информации о правильности
        answers_public = [
            {
                "id": answer.id,
                "answer_text": answer.answer_text,
                "order": answer.order
            }
            for answer in answers
        ]

        questions_public.append({
            "id": question.id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "order": question.order,
            "points": question.points,
            "image_url": question.image_url,
            "answers": answers_public
        })

        total_points += question.points

    return QuizResponsePublic(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        lesson_id=quiz.lesson_id,
        passing_score=quiz.passing_score,
        time_limit=quiz.time_limit,
        max_attempts=quiz.max_attempts,
        show_correct_answers=quiz.show_correct_answers,
        randomize_questions=quiz.randomize_questions,
        randomize_answers=quiz.randomize_answers,
        is_published=quiz.is_published,
        total_questions=len(questions_public),
        total_points=total_points,
        questions=questions_public
    )


@router.post("/submit", response_model=QuizAttemptResult)
def submit_quiz(
        submission: QuizAttemptSubmit,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Отправить ответы на квиз и получить результат

    - **quiz_id**: ID квиза
    - **answers**: Список ответов [{question_id: int, answer_ids: [int]}]
    - **time_spent**: Время в секундах
    """
    quiz = db.query(Quiz).options(
        joinedload(Quiz.questions).joinedload(QuizQuestion.answers)
    ).filter(Quiz.id == submission.quiz_id).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Квиз не найден")

    # Проверяем доступ
    lesson = db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == lesson.course_id,
        Enrollment.status == EnrollmentStatus.ACTIVE
    ).first()

    if not enrollment:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    # Проверяем количество попыток
    attempts_count = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.quiz_id == submission.quiz_id,
        QuizAttempt.completed_at.isnot(None)
    ).count()

    if attempts_count >= quiz.max_attempts:
        raise HTTPException(
            status_code=403,
            detail=f"Превышено максимальное количество попыток"
        )

    # Проверяем ответы и считаем баллы
    total_score = 0.0
    max_score = 0.0
    questions_results = []

    # Преобразуем ответы студента в словарь для быстрого доступа
    student_answers_dict = {
        ans.question_id: ans.answer_ids
        for ans in submission.answers
    }

    for question in quiz.questions:
        max_score += question.points

        # Получаем правильные ответы
        correct_answer_ids = [
            answer.id for answer in question.answers
            if answer.is_correct
        ]

        # Получаем ответы студента
        student_answer_ids = student_answers_dict.get(question.id, [])

        # Проверяем правильность
        is_correct = set(student_answer_ids) == set(correct_answer_ids)
        earned_points = question.points if is_correct else 0.0
        total_score += earned_points

        questions_results.append(QuestionResult(
            question_id=question.id,
            question_text=question.question_text,
            question_type=question.question_type,
            points=question.points,
            earned_points=earned_points,
            is_correct=is_correct,
            student_answers=student_answer_ids,
            correct_answers=correct_answer_ids,
            explanation=question.explanation
        ))

    # Вычисляем процент
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    is_passed = percentage >= quiz.passing_score

    # Сохраняем попытку
    attempt = QuizAttempt(
        student_id=current_user.id,
        quiz_id=submission.quiz_id,
        score=total_score,
        max_score=max_score,
        percentage=round(percentage, 2),
        is_passed=is_passed,
        answers=student_answers_dict,
        time_spent=submission.time_spent,
        completed_at=datetime.utcnow()
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # Возвращаем результат
    result = QuizAttemptResult(
        id=attempt.id,
        quiz_id=quiz.id,
        quiz_title=quiz.title,
        score=total_score,
        max_score=max_score,
        percentage=round(percentage, 2),
        is_passed=is_passed,
        time_spent=submission.time_spent,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        questions_results=questions_results if quiz.show_correct_answers else []
    )

    return result


@router.get("/{quiz_id}/attempts", response_model=List[QuizAttemptResponse])
def get_my_attempts(
        quiz_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить все мои попытки прохождения квиза
    """
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.quiz_id == quiz_id
    ).order_by(QuizAttempt.started_at.desc()).all()

    return attempts


@router.get("/attempts/{attempt_id}", response_model=QuizAttemptResult)
def get_attempt_details(
        attempt_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить детальные результаты попытки
    """
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="Попытка не найдена")

    # Проверяем права доступа
    if attempt.student_id != current_user.id:
        # Проверяем, является ли пользователь инструктором курса
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        lesson = db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()

        if lesson.course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Доступ запрещен")

    # Получаем квиз с вопросами
    quiz = db.query(Quiz).options(
        joinedload(Quiz.questions).joinedload(QuizQuestion.answers)
    ).filter(Quiz.id == attempt.quiz_id).first()

    # Формируем результаты по вопросам
    questions_results = []
    student_answers_dict = attempt.answers or {}

    for question in quiz.questions:
        correct_answer_ids = [
            answer.id for answer in question.answers
            if answer.is_correct
        ]

        student_answer_ids = student_answers_dict.get(str(question.id), [])
        is_correct = set(student_answer_ids) == set(correct_answer_ids)
        earned_points = question.points if is_correct else 0.0

        questions_results.append(QuestionResult(
            question_id=question.id,
            question_text=question.question_text,
            question_type=question.question_type,
            points=question.points,
            earned_points=earned_points,
            is_correct=is_correct,
            student_answers=student_answer_ids,
            correct_answers=correct_answer_ids,
            explanation=question.explanation
        ))

    return QuizAttemptResult(
        id=attempt.id,
        quiz_id=quiz.id,
        quiz_title=quiz.title,
        score=attempt.score,
        max_score=attempt.max_score,
        percentage=attempt.percentage,
        is_passed=attempt.is_passed,
        time_spent=attempt.time_spent,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        questions_results=questions_results
    )


# ============ СТАТИСТИКА (Инструктор) ============

@router.get("/{quiz_id}/statistics", response_model=QuizStatistics)
def get_quiz_statistics(
        quiz_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить статистику по квизу (только инструктор)

    - Общее количество попыток
    - Количество успешных/неуспешных попыток
    - Средний балл
    - Среднее время прохождения
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Квиз не найден")

    # Проверяем права
    lesson = db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()
    if lesson.course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    # Считаем статистику
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.completed_at.isnot(None)
    ).all()

    if not attempts:
        return QuizStatistics(
            quiz_id=quiz_id,
            quiz_title=quiz.title,
            total_attempts=0,
            passed_attempts=0,
            failed_attempts=0,
            average_score=0.0,
            average_time=0,
            best_score=0.0,
            worst_score=0.0
        )

    total_attempts = len(attempts)
    passed_attempts = sum(1 for a in attempts if a.is_passed)
    failed_attempts = total_attempts - passed_attempts

    scores = [a.percentage for a in attempts]
    times = [a.time_spent for a in attempts]

    average_score = sum(scores) / len(scores)
    average_time = sum(times) // len(times)
    best_score = max(scores)
    worst_score = min(scores)

    return QuizStatistics(
        quiz_id=quiz_id,
        quiz_title=quiz.title,
        total_attempts=total_attempts,
        passed_attempts=passed_attempts,
        failed_attempts=failed_attempts,
        average_score=round(average_score, 2),
        average_time=average_time,
        best_score=round(best_score, 2),
        worst_score=round(worst_score, 2)
    )


@router.get("/{quiz_id}/all-attempts", response_model=List[QuizAttemptResponse])
def get_all_quiz_attempts(
        quiz_id: int,
        limit: int = 50,
        offset: int = 0,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получить все попытки прохождения квиза (только инструктор)
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Квиз не найден")

    # Проверяем права
    lesson = db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()
    if lesson.course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.completed_at.isnot(None)
    ).order_by(
        QuizAttempt.completed_at.desc()
    ).limit(limit).offset(offset).all()

    return attempts