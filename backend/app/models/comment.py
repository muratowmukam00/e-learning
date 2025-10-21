from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    # Контент комментария
    content = Column(Text, nullable=False)

    # Автор комментария
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # К какому уроку относится
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)

    # Родительский комментарий (для ответов)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    # Модерация
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="comments")
    lesson = relationship("Lesson", back_populates="comments")

    # Ответы на комментарий
    replies = relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    parent = relationship("Comment", back_populates="replies", remote_side=[id])

    def __repr__(self):
        return f"<Comment {self.id} by User:{self.user_id}>"