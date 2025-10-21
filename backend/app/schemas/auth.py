from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole


# Схема для входа
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Схема для токенов
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Схема для refresh токена
class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Схема для ответа при входе/регистрации
class AuthResponse(BaseModel):
    user: dict
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Схема для payload токена
class TokenPayload(BaseModel):
    sub: Optional[int] = None  # user_id
    email: Optional[str] = None
    role: Optional[UserRole] = None
    exp: Optional[int] = None


# Схема для восстановления пароля
class PasswordResetRequest(BaseModel):
    email: EmailStr


# Схема для установки нового пароля
class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)