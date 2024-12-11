from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from .database import engine, get_db
from . import models, crud, utils, schemas
from datetime import date

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

models.Base.metadata.create_all(bind=engine)


@app.post("/register/", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate,
                  db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400,
                            detail="Email already registered")
    hashed_password = utils.hash_password(user.password)
    new_user = crud.create_user(db, name=user.name,
                                email=user.email,
                                password=hashed_password)
    return new_user


@app.post("/login/")
def login(request: Request,
          form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not utils.verify_password(form_data.password,
                                             user.hashed_password):
        raise HTTPException(status_code=401,
                            detail="Incorrect email or password")
    request.session["user_id"] = user.id
    return {"message": "Login successful"}


@app.post("/logout/")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logout successful"}


@app.get("/users/me/", response_model=schemas.UserResponse)
def read_users_me(request: Request,
                  db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401,
                            detail="Not authenticated")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404,
                            detail="User not found")
    return user


@app.put("/users/me/edit_password/", response_model=schemas.UserResponse)
def update_users_password(request: Request,
                          password_update: schemas.PasswordUpdate,
                          db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401,
                            detail="Not authenticated")
    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404,
                            detail="User not found")
    hashed_password = utils.hash_password(password_update.new_password)
    user = crud.update_user_password(db=db, user_id=user_id,
                                     new_password=hashed_password)
    return user


@app.put("/users/me/edit/", response_model=schemas.UserResponse)
def update_users(request: Request,
                 user_update: schemas.UserUpdate,
                 db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401,
                            detail="Not authenticated")
    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404,
                            detail="User not found")
    user = crud.update_user(db=db,
                            user_id=user_id,
                            user_update=user_update)
    return user


# Получить все цели пользователя
@app.get("/goals/", response_model=list[schemas.GoalResponse])
def get_goals(request: Request,
              db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401,
                            detail="Not authenticated")
    goals = crud.get_user_goals(db, user_id)
    return goals


# Получить все задачи пользователя на определённую дату
@app.get("/tasks/", response_model=list[schemas.TaskResponse])
def get_tasks(request: Request,
              date: date,
              db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401,
                            detail="Not authenticated")
    tasks = crud.get_user_tasks_by_date(db, user_id, date)
    return tasks
