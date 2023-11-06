from fastapi import Depends, HTTPException, status
from sqlalchemy import Time, cast
from models import Task, get_db
from routers.document_scheme import TaskDetail
from routers.user_controller import get_current_user
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


# def created_document(request,id:int,db):
#     """create the document on request and return the status.
#     Param:
#         request:Task schema
#         db:session of database
#         id: id of current user
#     Return:
#         status:The status of response
#         message: Response message
#         error:return the error status
#     """
#     doc = Task(name=request.name,content=request.content,user_id=id,status="Not Completed")
#     db.add(doc)
#     db.commit()
def create_task(task_data, db, id: int):
    try:
        new_task = Task(
            task_name=task_data.task_name,
            task_date=task_data.task_date,
            task_time=task_data.task_time,
            priority=task_data.priority,
            created_time=datetime.utcnow(),
            user_id=id,
            is_complete="Not Completed",
        )
        db.add(new_task)
        db.commit()

        return {
            "status": "success",
            "message": "successfully created a document",
            "data": [],
            "error": False,
        }
    except SQLAlchemyError as e:
        # Handle SQLAlchemy database-related exceptions
        print(f"Database Exception: {e}")
        raise HTTPException(status_code=500, detail="Failed to create task")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create task")


def update_func(id: int, db):
    """For changing to status completed the task."""
    db.query(Task).filter(Task.id == id).update(
        {Task.is_complete: "Completed"}, synchronize_session=False
    )
    db.commit()
    return {
        "status": "success",
        "message": "successfully updated task completion.",
        "data": [],
        "error": False,
    }


def sort_tasks(db, ids):
    tasks = (
        db.query(Task)
        .filter(Task.user_id == ids)
        .order_by(Task.task_date, Task.task_time)
        .all()
    )
    sorted_tasks = []
    for task in tasks:
        sorted_tasks.append(
            {
                "task_name": task.task_name,
                "task_date": task.task_date,
                "task_time": task.task_time,
                "priority": task.priority,
                "created_time": task.created_time,
                "is_complete": task.is_complete,
            }
        )

    return sorted_tasks


def update_det(task, task_data, db):
    task.task_name = task_data.task_name
    task.task_date = task_data.task_date
    task.priority = task_data.priority
    db.commit()

    # Return the updated task details
    return TaskDetail(
        task_name=task.task_name,
        task_date=task.task_date,
        task_time=task.task_time,
        priority=task.priority,
        created_time=task.created_time,
        is_complete=task.is_complete,
    )


def delete_rows(id: int, db):
    d = db.query(Task).filter(id == Task.id).first()
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Content")
    db.query(Task).filter(Task.id == id).delete(synchronize_session=False)
    db.commit()
    return {
        "status": "success",
        "message": "successfully deleted these rows",
        "data": "deleted",
        "error": False,
    }
