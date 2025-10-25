from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.course import router as courses_router
from app.api.category import router as categories_router
from app.api.lessons import router as lessons_router
from app.api.enrollments import router as enrollments_router
from app.api.reviews import router as reviews_router
from app.api.progress import router as progress_router
from app.api.comments import router as comments_router
from app.api.quiz import router as quiz_router
from app.api.users import router as users_router
from app.api.admin import router as admin_router
from app.database import engine, Base
from app.config import settings

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API для платформы онлайн-курсов по предпринимательству"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(courses_router, prefix="/api", tags=["Courses"])
app.include_router(categories_router, prefix="/api", tags=["Categories"])

app.include_router(lessons_router, prefix="/api", tags=["Lessons"])

app.include_router(enrollments_router, prefix="/api", tags=["Enrollments"])

app.include_router(reviews_router, prefix="/api", tags=["Reviews"])

app.include_router(progress_router, prefix="/api", tags=["Progress"])

app.include_router(comments_router, prefix="/api", tags=["Comments"])

app.include_router(quiz_router, prefix="/api", tags=["Quiz"])

app.include_router(users_router, prefix="/api", tags=["Users"])

app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Entrepreneurship Learning Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
