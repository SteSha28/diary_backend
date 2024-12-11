from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


class PasswordUpdate(BaseModel):
    new_password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None

    class Config:
        orm_mode = True


#  Mетки
class GoalBase(BaseModel):
    title: str


class GoalResponse(GoalBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class GoalCreate(GoalBase):
    description: Optional[str] = None


# Задача
class TaskBase(BaseModel):
    title: str
    due_date: Optional[date] = None
    goal_id: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class UserResponseWithTasks(UserBase):
    id: int
    tags: list[GoalResponse]
    tasks: list[TaskResponse]

    class Config:
        orm_mode = True
