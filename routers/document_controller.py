from datetime import datetime, timedelta
import models
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from models import RevokedToken, Task, Token, get_db
from passlib.context import CryptContext
from routers.authentication import authentic, token_authenticate
from routers.document_scheme import TaskCreate, TaskDetail, TaskUpdate, login
from service.create_document_service import (
    create_task,
    delete_rows,
    sort_tasks,
    update_det,
    update_func,
)
from sqlalchemy.orm import Session
from starlette import status
from routers.user_controller import create_users, refresh_tok, token_gen
from routers.user_schema import User

hashing = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
secret_key = "uisdfh9823h4rh4r8u34smkldnvvkndnoiebviewbufjcancciewc93ueu"
algorithm = "HS256"


router = APIRouter(prefix="/auth", tags=["auth"])
models.base.metadata.create_all(models.engine)


@router.post("/create_user")
def create_user(request: User, db: Session = Depends(get_db)):
    """To create a new user
    Param:
         request:The user schema.
         db:The session of database
    Return:
          status:The status of response
          message: Response message
          error:return the error status
    """
    s = create_users(request, db)
    return s


@router.post("/user_login")
async def user_login(formdata: login, db: Session = Depends(get_db)):
    """To login for the user.
    Params:
       formdata:Takes the username and the password from the input
       db:The session of the database
    Return:
        accesstoken,refreshtoken"""
    user = authentic(formdata.username, formdata.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    refresh_token = refresh_tok(user.name, user.id, timedelta(minutes=30), True)
    tokens = token_gen(user.name, user.id, timedelta(minutes=20))
    tok = Token(accesstype=tokens, user_id=user.id)
    db.add(tok)
    db.commit()
    return {"access_token": tokens, "refresh_token": refresh_token}


@router.post("/create_task")
async def create_tasks(
    request: TaskCreate,
    id: int = Depends(token_authenticate),
    db: Session = Depends(get_db),
):
    """To create documents of current authorized user
    Param:
        request:Document schema
        db:session of database
        id: id of current user
    Return:
        status:The status of response
        message: Response message
        error:return the error status
    """
    if not id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    s = create_task(request, db, id)
    return s


@router.get("/access_task/{id}")
async def access_document(
    id: int, db: Session = Depends(get_db), ids: int = Depends(token_authenticate)
):
    """To return specified task of given user.
    Params:
        id:accepts id of user in integer
        db:session of database
    Return:
        The data of user of given task id
    """
    if not ids:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    data = db.query(Task).filter(Task.user_id == ids, Task.id == id).all()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documents for user with ID {id} not found",
        )
    return data


@router.get("/task/sorting")
async def access_task(
    db: Session = Depends(get_db), ids: int = Depends(token_authenticate)
):
    """To return sorted tasks of given user.
    Params:
        db:session of database
    Return:
        The data of user sorted on scheduled date."""
    if not ids:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    s = sort_tasks(db, ids)
    return s


@router.put("/task/update_completion/{id}")
async def updated_value(
    id: int, db: Session = Depends(get_db), ids: int = Depends(token_authenticate)
):
    """To update the status to complete.
    Params:
        db:session of database
        id:id of the task for update
    Return:
        The update status"""
    if not ids:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    data = db.query(Task).filter(Task.id == id).all()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documents for user with ID {id} not found",
        )
    s = update_func(id, db)
    return s


@router.put("/tasks/update/{task_id}", response_model=TaskDetail)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    ids: int = Depends(token_authenticate),
):
    """
    To update the contents  inside task
    Params:
        db:Session of database
        taskdata:values to be updated
        task_id:id of the task for updation.
    Return:
         the updated task content.
    """
    if not ids:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    s = update_det(task, task_data, db)
    return s


@router.delete("/Documents/delete/{id}")
async def delete_row(
    id: int, db: Session = Depends(get_db), ids: int = Depends(token_authenticate)
):
    """To delete only specific task
    Params:
         db:Session of the database.
         id:id of the task we want to deleted
    Return:
         The status of delete.
    """
    if not ids:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    s = delete_rows(id, db)
    return s


@router.delete("/tasks/clear")
async def clear_all_tasks(
    db: Session = Depends(get_db), ids: int = Depends(token_authenticate)
):
    """To delete all the task
    Return:
     message:the delete status."""
    if not ids:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    tasks_to_delete = db.query(Task).all()
    if not tasks_to_delete:
        raise HTTPException(status_code=404, detail="No tasks to clear")
    for task in tasks_to_delete:
        db.delete(task)

    db.commit()

    return {"message": "All tasks cleared successfully"}


@router.post("/token/refresh")
async def refresh_access_token(
    refresh_token: str = Header(None), ids: int = Depends(token_authenticate)
):
    """For creating new access token
    Params:
        refresh_token:accepts the refresh token
    Return:
        return the new access token"""
    if not ids:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        payload = jwt.decode(refresh_token, secret_key, algorithms=algorithm)
        if payload.get("ref_token"):
            username = payload.get("name")
            userid = payload.get("id")
            expiration = timedelta(minutes=20)
            access_token = token_gen(username, userid, expiration)
            return {"access_token": access_token}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired"
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token"
    )


@router.post("/user_signout")
async def user_signout(request: Request, db: Session = Depends(get_db)):
    """
    To sign out a user by invalidating the token and checking if it's revoked.
    Params:
        request:The token fro the request header "Authorization".
    Return:
         The status of the output
    """
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided in headers")
    revoked_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()
    if revoked_token:
        raise HTTPException(status_code=401, detail="Token has already been revoked")
    revoked_token = RevokedToken(token=token)
    db.add(revoked_token)
    db.commit()

    return {"message": "User has been signed out"}
