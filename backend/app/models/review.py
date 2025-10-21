from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range'),
    )

    id = Column(Integer, primary_key=True, index=True)

    # Студент и курс
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # Оценка и отзыв
    rating = Column(Integer, nullable=False)  # 1-5 звезд
    title = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("User", back_populates="reviews")
    course = relationship("Course", back_populates="reviews")

    def __repr__(self):
        return f"<Review Student:{self.student_id} Course:{self.course_id} Rating:{self.rating}>"