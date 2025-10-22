from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, Float, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)

    # Студент и урок
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)

    # Статус прохождения
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)  # Для видео: сколько просмотрено

    # Время обучения
    time_spent = Column(Integer, default=0)  # Время в секундах

    # Временные метки
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("User", back_populates="progress_records")
    lesson = relationship("Lesson", back_populates="progress_records")

    def __repr__(self):
        return f"<Progress Student:{self.student_id} Lesson:{self.lesson_id}>"