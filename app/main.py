from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from .database import engine, get_db
from . import models, crud, utils, schemas
from datetime import date, timezone

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Настройка CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # Указываем адрес фронтенда React
#     allow_credentials=True,
#     allow_methods=["*"],  # Разрешаем все методы
#     allow_headers=["*"],  # Разрешаем все заголовки
# )

models.Base.metadata.create_all(bind=engine)


def get_current_user_id(request: Request) -> int:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id


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


@app.post("/login/", response_model=schemas.UserResponse)
def login(request: Request,
          form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not utils.verify_password(form_data.password,
                                             user.hashed_password):
        raise HTTPException(status_code=401,
                            detail="Incorrect email or password")
    request.session["user_id"] = user.id
    return user


@app.post("/logout/")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logout successful"}


# Возвращает данные юзера, его теги и задачи.
@app.get("/users/me/", response_model=schemas.UserResponseWithTasks)
def read_users_me(request: Request,
                  db: Session = Depends(get_db),
                  user_id: int = Depends(get_current_user_id)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404,
                            detail="User not found")
    tags = crud.get_user_goals(db, user_id)
    tasks = crud.get_user_active_tasks(db, user_id)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "tags": tags,
        "tasks": tasks,
    }


# Редактирование пароля, возвращает юзера.
@app.put("/users/me/edit_password/", response_model=schemas.UserResponse)
def update_users_password(request: Request,
                          password_update: schemas.PasswordUpdate,
                          db: Session = Depends(get_db),
                          user_id: int = Depends(get_current_user_id)):
    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404,
                            detail="User not found")
    hashed_password = utils.hash_password(password_update.new_password)
    user = crud.update_user_password(db=db, user_id=user_id,
                                     new_password=hashed_password)
    return user


# Редактирование юзера, возвращает юзера.
@app.put("/users/me/edit/", response_model=schemas.UserResponse)
def update_users(request: Request,
                 user_update: schemas.UserUpdate,
                 db: Session = Depends(get_db),
                 user_id: int = Depends(get_current_user_id)):
    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404,
                            detail="User not found")
    user = crud.update_user(db=db,
                            user_id=user_id,
                            user_update=user_update)
    return user


# Получить все теги пользователя.
@app.get("/tags/", response_model=list[schemas.GoalResponse])
def get_tags(request: Request,
             db: Session = Depends(get_db),
             user_id: int = Depends(get_current_user_id)):
    goals = crud.get_user_goals(db, user_id)
    return goals


# Создать тег, возвращает все теги.
@app.post("/tags/", response_model=list[schemas.GoalResponse])
def create_tags(request: Request,
                tag: schemas.GoalCreate,
                db: Session = Depends(get_db),
                user_id: int = Depends(get_current_user_id)):
    crud.create_goal(db=db, goal=tag, user_id=user_id)
    tags = crud.get_user_goals(db, user_id)
    return tags


# Удалить тег, возвращает все теги.
@app.delete("/tags/{tag_id}/", response_model=list[schemas.GoalResponse])
def delete_tags(request: Request,
                tag_id,
                db: Session = Depends(get_db),
                user_id: int = Depends(get_current_user_id)):
    crud.delete_goal(db=db, goal_id=tag_id)
    tags = crud.get_user_goals(db, user_id)
    return tags


# Получить все задачи по тегу.
@app.get("/tags/{tag_id}/", response_model=list[schemas.TaskResponse])
def get_tasks_by_tag(request: Request,
                     tag_id: int,
                     db: Session = Depends(get_db),
                     user_id: int = Depends(get_current_user_id)):
    tasks = crud.get_user_tasks_by_tag(db, user_id, tag_id)
    return tasks


# Создать задачу, возвращает созданную задачу
@app.post("/tasks/", response_model=schemas.TaskResponse)
def get_tasks(request: Request,
              task: schemas.TaskBase,
              db: Session = Depends(get_db),
              user_id: int = Depends(get_current_user_id)):
    task = crud.create_task(db, task, user_id)
    return task


# Возвращает все задачи на текущий день
@app.get("/tasks/today/", response_model=list[schemas.TaskResponse])
def get_today_tasks(request: Request,
                    db: Session = Depends(get_db),
                    user_id: int = Depends(get_current_user_id)):
    today = date.today()
    tasks = crud.get_user_tasks_by_date(db, user_id, today)
    return tasks


# Возвращает все задачи за указанный период
@app.get("/tasks/period/", response_model=list[schemas.TaskResponse])
def get_pediod_tasks(request: Request,
                     db: Session = Depends(get_db),
                     user_id: int = Depends(get_current_user_id),
                     start_day: date = Query(),
                     end_day: date = Query()):
    tasks = crud.get_user_tasks_by_period(db, user_id, start_day, end_day)
    return tasks


# Страница задачи, возвращает задачу.
@app.get("/tasks/{task_id}/", response_model=schemas.TaskResponse)
def get_task_by_id(request: Request,
                   task_id: int,
                   db: Session = Depends(get_db),
                   user_id: int = Depends(get_current_user_id)):
    task = crud.get_user_tasks_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404,
                            detail="Task not found")
    return task


# Редактирование задачи, возвращает задачу.
@app.put("/tasks/{task_id}/", response_model=schemas.TaskResponse)
def update_task(request: Request,
                task_id: int,
                task_update: schemas.TaskUpdate,
                db: Session = Depends(get_db),
                user_id: int = Depends(get_current_user_id)):
    task = crud.update_task(db, task_id, task_update)
    return task


# Удаление задачи, возвращает сообщение.
@app.delete("/tasks/{task_id}/")
def delete_task(request: Request,
                task_id: int,
                db: Session = Depends(get_db),
                user_id: int = Depends(get_current_user_id)):
    task = crud.delete_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404,
                            detail="Task not found")
    return {"message": "Task deleted"}
