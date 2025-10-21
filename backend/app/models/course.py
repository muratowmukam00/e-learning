from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class CourseLevel(str, enum.Enum):
    """Уровень сложности курса"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseStatus(str, enum.Enum):
    """Статус курса"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)

    # Основная информация
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    short_description = Column(String(500), nullable=True)

    # Медиа
    thumbnail_url = Column(String, nullable=True)
    preview_video_url = Column(String, nullable=True)

    # Детали курса
    level = Column(Enum(CourseLevel), default=CourseLevel.BEGINNER)
    language = Column(String(50), default="ru")
    duration_hours = Column(Float, default=0.0)  # Общая длительность в часах

    # Цена
    price = Column(Float, default=0.0)  # 0 = бесплатный курс
    discount_price = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")

    # Статус и видимость
    status = Column(Enum(CourseStatus), default=CourseStatus.DRAFT)
    is_published = Column(Boolean, default=False)

    # Категория
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # Преподаватель
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Требования и цели
    requirements = Column(Text, nullable=True)  # JSON или текст
    learning_outcomes = Column(Text, nullable=True)  # JSON или текст
    target_audience = Column(Text, nullable=True)

    # Статистика
    total_students = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    total_lessons = Column(Integer, default=0)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    instructor = relationship("User", back_populates="created_courses", foreign_keys=[instructor_id])
    category = relationship("Category", back_populates="courses")
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course {self.title}>"

    @property
    def is_free(self):
        return self.price == 0.0

    @property
    def effective_price(self):
        """Возвращает цену со скидкой, если есть"""
        return self.discount_price if self.discount_price else self.price