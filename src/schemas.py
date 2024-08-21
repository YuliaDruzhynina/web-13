import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from src.entity.models import Role


class ContactSchema(BaseModel):
    fullname: str
    email: EmailStr
    phone_number: str
    birthday: datetime.date

    class Config:
        from_attributes = True


class UserModel(BaseModel):
    username: str
    email: EmailStr
    password: str
    # refresh_token: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr
    avatar: Optional[str]
    detail: str = "User successfully created"
    role: Optional[Role]

    class Config:
        from_attributes = True


class ContactResponse(ContactSchema):
    id: int
    user: Optional[UserResponse]

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class EmailSchema(BaseModel):
    email: EmailStr
