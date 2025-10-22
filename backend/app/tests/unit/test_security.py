from datetime import timedelta
from jose import jwt
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.config import settings


def test_password_hash_and_verify():
    """Проверяет корректность хеширования и верификации пароля"""
    password = "strongpassword123"
    hashed = get_password_hash(password)

    # Хеш не должен быть равен исходному паролю
    assert hashed != password
    # Проверяем верификацию
    assert verify_password(password, hashed)
    # Проверяем ложный пароль
    assert not verify_password("wrongpassword", hashed)


def test_create_access_token():
    """Создание и валидация access token"""
    data = {"user_id": 42}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))

    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["user_id"] == 42
    assert decoded["type"] == "access"
    assert "exp" in decoded


def test_create_refresh_token():
    """Создание и валидация refresh token"""
    data = {"user_id": 99}
    token = create_refresh_token(data)

    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["user_id"] == 99
    assert decoded["type"] == "refresh"
    assert "exp" in decoded


def test_decode_token_invalid():
    """Декодирование некорректного токена должно вернуть None"""
    invalid_token = "this.is.not.a.valid.token"
    decoded = decode_token(invalid_token)
    assert decoded is None
