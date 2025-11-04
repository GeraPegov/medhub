from pydantic import BaseModel, Field, field_validator, EmailStr
import re
from typing import Optional


class ArticleCreateDTO(BaseModel):
    author: str
    title: str = Field(min_length=3, max_length=200)
    content: Optional[str] = Field(min_length=10, max_length=10000)

class ArticleRegisterDTO(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, max_length=100, description="Пароль")
    password_confirm: str = Field(..., description="Подтверждение пароля")

    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        # Проверка на временные email сервисы
        temporary_domains = [
            'temp-mail.org', '10minutemail.com', 'guerrillamail.com',
            'yopmail.com', 'mailinator.com', 'trashmail.com'
        ]
        domain = v.split('@')[-1].lower()
        if any(temp_domain in domain for temp_domain in temporary_domains):
            raise ValueError('Временные email адреса не поддерживаются')
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Валидация сложности пароля"""
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')

        errors = []

        # Проверка на заглавные буквы
        if not any(c.isupper() for c in v):
            errors.append('хотя бы одну заглавную букву')

        # Проверка на строчные буквы
        if not any(c.islower() for c in v):
            errors.append('хотя бы одну строчную букву')

        # Проверка на цифры
        if not any(c.isdigit() for c in v):
            errors.append('хотя бы одну цифру')

        # Проверка на простые пароли
        weak_passwords = [
            'password', '12345678', 'qwertyui', 'admin123',
            'password123', 'abc12345', '11111111'
        ]
        if v.lower() in weak_passwords:
            errors.append('более сложную комбинацию')

        if errors:
            raise ValueError(f'Пароль должен содержать: {", ".join(errors)}')

        return v

    @field_validator('password_confirm')
    @classmethod
    def validate_password_match(cls, v: str, info) -> str:
        """Проверка совпадения паролей"""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Пароли не совпадают')
        return v
