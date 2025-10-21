from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Импорты будут добавлены позже
# from app.database import engine, Base
# from app.api import auth, users, courses, lessons

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: создание таблиц БД
    print("🚀 Starting up...")
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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
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

# Подключение роутеров (будет добавлено позже)
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(users.router, prefix="/api/users", tags=["Users"])
# app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
# app.include_router(lessons.router, prefix="/api/lessons", tags=["Lessons"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)