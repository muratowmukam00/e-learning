from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, Boolean, Enum, String, func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class EnrollmentStatus(str, enum.Enum):
    """Статус записи на курс"""
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    EXPIRED = "expired"


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)

    # Студент и курс
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # Статус
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)

    # Прогресс
    progress_percentage = Column(Float, default=0.0)  # 0-100%
    completed_lessons = Column(Integer, default=0)

    # Оплата
    price_paid = Column(Float, default=0.0)  # Цена, которую заплатил студент
    is_paid = Column(Boolean, default=False)

    # Сертификат
    certificate_url = Column(String, nullable=True)
    certificate_issued_at = Column(DateTime, nullable=True)

    # Временные метки
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment Student:{self.student_id} Course:{self.course_id}>"

    @property
    def is_completed(self):
        return self.status == EnrollmentStatus.COMPLETED