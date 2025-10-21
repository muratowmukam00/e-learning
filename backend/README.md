# Backend - Платформа онлайн-курсов по предпринимательству

FastAPI backend для интерактивной платформы онлайн-обучения.

## 🚀 Быстрый старт

### 1. Создание виртуального окружения

```bash
# Если еще не создано
python -m venv .venv

# Активация (Linux/Mac)
source .venv/bin/activate

# Активация (Windows)
.venv\Scripts\activate
```

### 2. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 3. Настройка базы данных

**Установите PostgreSQL:**
- Linux: `sudo apt install postgresql postgresql-contrib`
- Mac: `brew install postgresql`
- Windows: Скачайте с официального сайта

**Создайте базу данных:**

```bash
# Войдите в PostgreSQL
sudo -u postgres psql

# Создайте пользователя и БД
CREATE USER courseuser WITH PASSWORD 'coursepass';
CREATE DATABASE entrepreneurship_courses OWNER courseuser;
GRANT ALL PRIVILEGES ON DATABASE entrepreneurship_courses TO courseuser;

# Выход
\q
```

### 4. Настройка переменных окружения

```bash
# Скопируйте файл с примером
cp .env.example .env

# Отредактируйте .env и установите свои значения
nano .env
```

**Обязательно измените:**
- `DATABASE_URL` - URL подключения к вашей БД
- `SECRET_KEY` - сгенерируйте случайный ключ (минимум 32 символа)

**Генерация SECRET_KEY:**
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Создание структуры папок

```bash
cd backend

# Создайте необходимые папки
mkdir -p app/models app/schemas app/api app/services app/utils

# Создайте пустые __init__.py файлы
touch app/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/api/__init__.py
touch app/services/__init__.py
touch app/utils/__init__.py
```

### 6. Запуск сервера

```bash
# Из папки backend
python main.py

# Или через uvicorn напрямую
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Сервер будет доступен по адресу: `http://localhost:8000`

## 📚 API Документация

После запуска сервера, документация доступна по адресам:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🗂️ Структура проекта

```
backend/
├── main.py                 # Точка входа приложения
├── requirements.txt        # Зависимости Python
├── .env                    # Переменные окружения (не коммитить!)
├── .env.example           # Пример переменных окружения
├── ROADMAP.md             # План разработки
├── README.md              # Эта инструкция
│
└── app/
    ├── __init__.py
    ├── config.py          # Конфигурация приложения
    ├── database.py        # Подключение к БД
    │
    ├── models/            # SQLAlchemy модели
    │   ├── __init__.py
    │   ├── user.py       # (будет создано)
    │   ├── course.py     # (будет создано)
    │   └── ...
    │
    ├── schemas/           # Pydantic схемы
    │   ├── __init__.py
    │   ├── user.py       # (будет создано)
    │   └── ...
    │
    ├── api/               # API endpoints
    │   ├── __init__.py
    │   ├── auth.py       # (будет создано)
    │   └── ...
    │
    ├── services/          # Бизнес-логика
    │   ├── __init__.py
    │   └── ...
    │
    └── utils/             # Утилиты
        ├── __init__.py
        ├── security.py    # JWT, хеширование
        └── ...
```

## 🔧 Следующие шаги

1. **Создать модели БД:**
   - User (пользователи)
   - Course (курсы)
   - Lesson (уроки)
   - Enrollment (записи на курсы)
   - Progress (прогресс обучения)

2. **Настроить Alembic для миграций:**
   ```bash
   alembic init alembic
   ```

3. **Создать API endpoints:**
   - Аутентификация (регистрация, вход)
   - CRUD для курсов
   - CRUD для уроков
   - Управление записями

4. **Добавить тесты**

## ⚙️ Полезные команды

```bash
# Обновление зависимостей
pip install --upgrade -r requirements.txt

# Заморозка зависимостей
pip freeze > requirements.txt

# Запуск с автоперезагрузкой
uvicorn main:app --reload

# Запуск на другом порту
uvicorn main:app --port 8001

# Создание миграции (когда настроите Alembic)
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head
```

## 🐛 Отладка

Если возникают ошибки:

1. **Проблемы с подключением к БД:**
   - Проверьте, что PostgreSQL запущен: `sudo systemctl status postgresql`
   - Проверьте DATABASE_URL в .env
   - Проверьте права пользователя БД

2. **Import ошибки:**
   - Убедитесь, что все `__init__.py` файлы созданы
   - Проверьте, что виртуальное окружение активировано

3. **JWT ошибки:**
   - Проверьте, что SECRET_KEY установлен в .env
   - Убедитесь, что ключ достаточно длинный (32+ символа)

## 📝 Логи

Логи SQL запросов доступны в консоли при `DEBUG=True` в .env

## 🔒 Безопасность

- ✅ Никогда не коммитьте `.env` файл
- ✅ Используйте сильные пароли для БД
- ✅ Генерируйте уникальный SECRET_KEY для каждого окружения
- ✅ В продакшене установите `DEBUG=False`

## 📞 Контакты

Для вопросов по проекту обратитесь к разработчику.