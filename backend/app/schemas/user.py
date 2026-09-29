from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "Admin"
    TECHNICIAN = "Technician"
    EMPLOYEE = "Employee"


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    id: int
    name: str
    email: EmailStr
    role: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    role: UserRole