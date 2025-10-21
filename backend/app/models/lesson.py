from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class LessonType(str, enum.Enum):
    """Тип урока"""
    VIDEO = "video"
    TEXT = "text"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    RESOURCE = "resource"


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)

    # Основная информация
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Принадлежность к курсу
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # Порядок урока в курсе
    order = Column(Integer, nullable=False)

    # Тип и контент
    lesson_type = Column(Enum(LessonType), default=LessonType.VIDEO)
    content = Column(Text, nullable=True)  # HTML/Markdown контент для текстовых уроков

    # Видео
    video_url = Column(String, nullable=True)  # YouTube, Vimeo и т.д.
    video_duration = Column(Float, nullable=True)  # Длительность в минутах

    # Файлы
    resources_urls = Column(Text, nullable=True)  # JSON список файлов для скачивания

    # Доступность
    is_free_preview = Column(Boolean, default=False)  # Бесплатный урок для предпросмотра
    is_published = Column(Boolean, default=True)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="lessons")
    progress_records = relationship("Progress", back_populates="lesson")
    comments = relationship("Comment", back_populates="lesson", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Lesson {self.title} (Course: {self.course_id})>"