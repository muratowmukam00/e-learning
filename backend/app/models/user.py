from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """Роли пользователей в системе"""
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Личная информация
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)

    # Роль и статус
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    # Курсы, созданные этим пользователем (если instructor)
    created_courses = relationship("Course", back_populates="instructor", foreign_keys="Course.instructor_id")

    # Записи на курсы (если student)
    enrollments = relationship("Enrollment", back_populates="student")

    # Прогресс обучения
    progress_records = relationship("Progress", back_populates="student")

    # Отзывы
    reviews = relationship("Review", back_populates="student")
    comments = relationship("Comment", back_populates="user")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"