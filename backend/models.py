from __future__ import annotations

from datetime import datetime, timezone, date as DateValue, time as TimeValue
from enum import Enum

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"


class ProdusBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    description: str = Field(min_length=1, max_length=500)
    image: str = Field(min_length=1, max_length=500)
    alt: str = Field(min_length=1, max_length=200)
    isFeatured: bool = False

    @field_validator("name", "category", "description", "image", "alt")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        trimmed_value = value.strip()
        if not trimmed_value:
            raise ValueError("Value cannot be blank.")
        return trimmed_value


class Produs(ProdusBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ProdusCreate(ProdusBase):
    pass


class ProdusUpdate(ProdusBase):
    pass


class ComandaBaza(SQLModel):
    contact_name: str = Field(min_length=1, max_length=100)
    contact_email: EmailStr
    contact_phone: str = Field(min_length=6, max_length=20)
    delivery_address: str = Field(min_length=5, max_length=300)
    produs_id: int
    quantity: int = Field(ge=1, le=10)
    special_requests: str | None = Field(default=None, max_length=500)


class Comanda(ComandaBaza, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: str = Field(default="pending", index=True) # pending, processing, shipped, delivered, cancelled
    created_at: datetime = Field(default_factory=utc_now)


class ComandaCreare(ComandaBaza):
    pass


class MesajContact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nume: str = Field(min_length=1, max_length=100)
    telefon: str = Field(default="", min_length=0, max_length=20)
    email: EmailStr
    mesaj: str = Field(min_length=1, max_length=1000)
    created_at: datetime = Field(default_factory=utc_now)


class UserBase(SQLModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=100)
    role: UserRole = UserRole.manager
    is_active: bool = True


class User(UserBase, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class StaffUserCreate(SQLModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.manager


class StaffUserRead(UserBase):
    id: int
    created_at: datetime


class LoginRequest(SQLModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserSession(SQLModel, table=True):
    __tablename__ = "user_sessions"
    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=utc_now)
    expires_at: datetime
    revoked_at: datetime | None = Field(default=None)


class SessionResponse(SQLModel):
    session_token: str
    user: StaffUserRead
