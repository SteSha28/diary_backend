from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, Date
)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    goals = relationship("Goal",
                         back_populates="user",
                         cascade="all, delete-orphan")
    tasks = relationship("Task",
                         back_populates="user",
                         cascade="all, delete-orphan")


# Категория
class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer,
                     ForeignKey("users.id"),
                     nullable=False)

    user = relationship("User",
                        back_populates="goals")

    tasks = relationship("Task",
                         back_populates="goal",
                         cascade="all, delete-orphan")


# Задача
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    is_completed = Column(Integer, default=0)
    user_id = Column(Integer,
                     ForeignKey("users.id"),
                     nullable=False)
    goal_id = Column(Integer,
                     ForeignKey("goals.id"),
                     nullable=True)

    user = relationship("User",
                        back_populates="tasks")

    goal = relationship("Goal",
                        back_populates="tasks")
