from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class QuizType(str, enum.Enum):
    """Тип квиза"""
    MULTIPLE_CHOICE = "multiple_choice"  # Один правильный ответ
    MULTIPLE_SELECT = "multiple_select"  # Несколько правильных ответов
    TRUE_FALSE = "true_false"  # Правда/Ложь
    SHORT_ANSWER = "short_answer"  # Короткий ответ (текст)


class Quiz(Base):
    """Квиз/Тест для урока"""
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)

    # Основная информация
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Связь с уроком
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)

    # Настройки квиза
    passing_score = Column(Float, default=70.0)  # Минимальный процент для прохождения
    time_limit = Column(Integer, nullable=True)  # Ограничение по времени в минутах
    max_attempts = Column(Integer, default=3)  # Максимальное количество попыток
    show_correct_answers = Column(Boolean, default=True)  # Показывать правильные ответы после прохождения
    randomize_questions = Column(Boolean, default=False)  # Случайный порядок вопросов
    randomize_answers = Column(Boolean, default=False)  # Случайный порядок ответов

    # Статус
    is_published = Column(Boolean, default=True)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lesson = relationship("Lesson", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quiz {self.title}>"


class QuizQuestion(Base):
    """Вопрос в квизе"""
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)

    # Связь с квизом
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)

    # Вопрос
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuizType), default=QuizType.MULTIPLE_CHOICE)

    # Порядок вопроса
    order = Column(Integer, default=0)

    # Баллы за вопрос
    points = Column(Float, default=1.0)

    # Пояснение (показывается после ответа)
    explanation = Column(Text, nullable=True)

    # Медиа (опционально)
    image_url = Column(String, nullable=True)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("QuizAnswer", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuizQuestion {self.id} in Quiz:{self.quiz_id}>"


class QuizAnswer(Base):
    """Вариант ответа на вопрос"""
    __tablename__ = "quiz_answers"

    id = Column(Integer, primary_key=True, index=True)

    # Связь с вопросом
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)

    # Текст ответа
    answer_text = Column(Text, nullable=False)

    # Правильный ли ответ
    is_correct = Column(Boolean, default=False)

    # Порядок ответа
    order = Column(Integer, default=0)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    question = relationship("QuizQuestion", back_populates="answers")

    def __repr__(self):
        return f"<QuizAnswer {self.id} ({'correct' if self.is_correct else 'incorrect'})>"


class QuizAttempt(Base):
    """Попытка прохождения квиза студентом"""
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)

    # Студент и квиз
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)

    # Результаты
    score = Column(Float, default=0.0)  # Набранные баллы
    max_score = Column(Float, default=0.0)  # Максимально возможные баллы
    percentage = Column(Float, default=0.0)  # Процент правильных ответов
    is_passed = Column(Boolean, default=False)  # Пройден ли тест

    # Ответы студента (JSON)
    answers = Column(JSON, nullable=True)  # {question_id: [answer_ids], ...}

    # Время прохождения
    time_spent = Column(Integer, default=0)  # Время в секундах

    # Временные метки
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")

    def __repr__(self):
        return f"<QuizAttempt Student:{self.student_id} Quiz:{self.quiz_id} Score:{self.percentage}%>"