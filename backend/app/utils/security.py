from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля хешу

    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Хешированный пароль

    Returns:
        True если пароль совпадает, False в противном случае
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хеширует пароль

    Args:
        password: Пароль в открытом виде

    Returns:
        Хешированный пароль
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT access token

    Args:
        data: Данные для включения в токен (обычно user_id, email)
        expires_delta: Время жизни токена

    Returns:
        JWT токен в виде строки
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Создает JWT refresh token с более длительным сроком действия

    Args:
        data: Данные для включения в токен

    Returns:
        JWT refresh токен
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Декодирует и валидирует JWT токен

    Args:
        token: JWT токен

    Returns:
        Payload токена или None если токен невалиден
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None