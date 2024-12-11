from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, name: str, email: str, password: str):
    user = models.User(name=name, email=email, hashed_password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session,
                         user_id: int,
                         new_password: schemas.PasswordUpdate):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    user.hashed_password = new_password
    db.commit()
    db.refresh(user)
    return user


def get_user_goals(db: Session, user_id: int):
    return db.query(models.Goal).filter(models.Goal.user_id == user_id).all()


def get_user_tasks_by_date(db: Session, user_id: int, task_date: date):
    return (
        db.query(models.Task)
        .filter(models.Task.user_id == user_id,
                models.Task.due_date == task_date)
        .all()
    )


def get_user_active_tasks(db: Session, user_id: int):
    return (
        db.query(models.Task)
        .filter(models.Task.user_id == user_id,
                models.Task.is_completed == 0)
        .all()
    )


def create_goal(db: Session, goal: schemas.GoalCreate, user_id: int):
    new_goal = models.Goal(
        title=goal.title,
        description=goal.description,
        user_id=user_id
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal


def delete_goal(db: Session, goal_id: int):
    goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if not goal:
        return False

    db.delete(goal)
    db.commit()
    return True
