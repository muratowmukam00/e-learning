from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import Base, engine

# Импорты моделей для создания таблиц
from app.models import (
    User, Course, Category, Lesson,
    Enrollment, Progress, Review
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: создание таблиц БД
    print("🚀 Starting up...")
    # Раскомментируйте когда будете готовы создать таблицы
    # Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    print("🛑 Shutting down...")

app = FastAPI(
    title="Платформа онлайн-курсов по предпринимательству",
    description="API для интерактивной платформы обучения",
    version="1.0.0",
    lifespan=lifespan
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в API платформы онлайн-курсов!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Подключение роутеров
from app.api import auth

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Будет добавлено позже:
# from app.api import users, courses, lessons
# app.include_router(users.router, prefix="/api/users", tags=["Users"])
# app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
# app.include_router(lessons.router, prefix="/api/lessons", tags=["Lessons"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)