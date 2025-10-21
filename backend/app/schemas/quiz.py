from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict
from app.models.quiz import QuizType


# ============ ANSWER SCHEMAS ============
class QuizAnswerBase(BaseModel):
    """Базовая схема ответа"""
    answer_text: str = Field(..., min_length=1, max_length=500)
    is_correct: bool = False
    order: int = 0


class QuizAnswerCreate(QuizAnswerBase):
    """Создание ответа"""
    pass


class QuizAnswerResponse(QuizAnswerBase):
    """Ответ с данными"""
    id: int
    question_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class QuizAnswerResponsePublic(BaseModel):
    """Публичный ответ (без is_correct для студента до завершения)"""
    id: int
    answer_text: str
    order: int

    class Config:
        from_attributes = True


# ============ QUESTION SCHEMAS ============
class QuizQuestionBase(BaseModel):
    """Базовая схема вопроса"""
    question_text: str = Field(..., min_length=5)
    question_type: QuizType = QuizType.MULTIPLE_CHOICE
    order: int = 0
    points: float = Field(1.0, ge=0.1)
    explanation: Optional[str] = None
    image_url: Optional[str] = None


class QuizQuestionCreate(QuizQuestionBase):
    """Создание вопроса с ответами"""
    answers: List[QuizAnswerCreate] = Field(..., min_items=2)


class QuizQuestionUpdate(BaseModel):
    """Обновление вопроса"""
    question_text: Optional[str] = Field(None, min_length=5)
    question_type: Optional[QuizType] = None
    order: Optional[int] = None
    points: Optional[float] = Field(None, ge=0.1)
    explanation: Optional[str] = None
    image_url: Optional[str] = None


class QuizQuestionResponse(QuizQuestionBase):
    """Ответ с вопросом (для инструктора - с правильными ответами)"""
    id: int
    quiz_id: int
    answers: List[QuizAnswerResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuizQuestionResponsePublic(BaseModel):
    """Публичный вопрос (для студента - без правильных ответов)"""
    id: int
    question_text: str
    question_type: QuizType
    order: int
    points: float
    image_url: Optional[str]
    answers: List[QuizAnswerResponsePublic]

    class Config:
        from_attributes = True


# ============ QUIZ SCHEMAS ============
class QuizBase(BaseModel):
    """Базовая схема квиза"""
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    passing_score: float = Field(70.0, ge=0, le=100)
    time_limit: Optional[int] = Field(None, ge=1)  # в минутах
    max_attempts: int = Field(3, ge=1)
    show_correct_answers: bool = True
    randomize_questions: bool = False
    randomize_answers: bool = False
    is_published: bool = True


class QuizCreate(QuizBase):
    """Создание квиза"""
    lesson_id: int


class QuizUpdate(BaseModel):
    """Обновление квиза"""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    passing_score: Optional[float] = Field(None, ge=0, le=100)
    time_limit: Optional[int] = Field(None, ge=1)
    max_attempts: Optional[int] = Field(None, ge=1)
    show_correct_answers: Optional[bool] = None
    randomize_questions: Optional[bool] = None
    randomize_answers: Optional[bool] = None
    is_published: Optional[bool] = None


class QuizResponse(QuizBase):
    """Полный ответ с квизом (для инструктора)"""
    id: int
    lesson_id: int
    questions: List[QuizQuestionResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuizResponsePublic(QuizBase):
    """Публичный квиз (для студента)"""
    id: int
    lesson_id: int
    total_questions: int
    total_points: float
    questions: List[QuizQuestionResponsePublic]

    class Config:
        from_attributes = True


class QuizListItem(BaseModel):
    """Элемент списка квизов"""
    id: int
    title: str
    description: Optional[str]
    lesson_id: int
    total_questions: int
    passing_score: float
    max_attempts: int
    is_published: bool

    class Config:
        from_attributes = True


# ============ ATTEMPT SCHEMAS ============
class QuizAttemptStart(BaseModel):
    """Начало попытки прохождения квиза"""
    quiz_id: int


class StudentAnswer(BaseModel):
    """Ответ студента на вопрос"""
    question_id: int
    answer_ids: List[int]  # Список ID выбранных ответов


class QuizAttemptSubmit(BaseModel):
    """Отправка ответов на квиз"""
    quiz_id: int
    answers: List[StudentAnswer]
    time_spent: int = Field(..., ge=0)  # в секундах


class QuestionResult(BaseModel):
    """Результат по вопросу"""
    question_id: int
    question_text: str
    question_type: QuizType
    points: float
    earned_points: float
    is_correct: bool
    student_answers: List[int]
    correct_answers: List[int]
    explanation: Optional[str]


class QuizAttemptResult(BaseModel):
    """Результат попытки"""
    id: int
    quiz_id: int
    quiz_title: str
    score: float
    max_score: float
    percentage: float
    is_passed: bool
    time_spent: int
    started_at: datetime
    completed_at: datetime
    questions_results: List[QuestionResult]

    class Config:
        from_attributes = True


class QuizAttemptResponse(BaseModel):
    """Ответ с попыткой (краткая версия)"""
    id: int
    quiz_id: int
    student_id: int
    score: float
    max_score: float
    percentage: float
    is_passed: bool
    time_spent: int
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class QuizStatistics(BaseModel):
    """Статистика по квизу"""
    quiz_id: int
    quiz_title: str
    total_attempts: int
    passed_attempts: int
    failed_attempts: int
    average_score: float
    average_time: int  # в секундах
    best_score: float
    worst_score: float