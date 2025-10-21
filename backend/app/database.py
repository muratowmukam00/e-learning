from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Создаем engine для подключения к БД
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    echo=settings.DEBUG  # Логирование SQL запросов в режиме DEBUG
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


# Dependency для получения сессии БД
def get_db():
    """
    Генератор сессии БД для использования в endpoints

    Использование:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Функция для создания всех таблиц
def create_tables():
    """
    Создает все таблицы в БД на основе моделей
    Используется при первом запуске или в тестах
    """
    Base.metadata.create_all(bind=engine)


# Функция для удаления всех таблиц (для тестов)
def drop_tables():
    """
    Удаляет все таблицы из БД
    Используется только в тестах
    """
    Base.metadata.drop_all(bind=engine)