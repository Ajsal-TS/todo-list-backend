from pydantic import BaseModel
from datetime import date, time


class login(BaseModel):
    username: str
    password: str


class TaskCreate(BaseModel):
    task_name: str
    task_date: date
    task_time: time
    priority: str


class TaskDetail(BaseModel):
    task_name: str
    task_date: date
    task_time: time
    priority: str
    is_complete: str = "Not Completed"


class TaskUpdate(BaseModel):
    task_name: str
    task_date: date
    priority: str
