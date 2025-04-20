from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO import taskDAO
#import Schema
from schemas.taskSchema import TaskSchema, TaskCreateSchema, TaskUpdateSchema, StatusEnum, PriorityEnum

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def getTasksPagination(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1), # page number, default is 1 and must be greater than 1
    pageSize: int = Query(10, ge=1, le= 100), # limit of items per page, default is 10 and must be between 1 and 100
    searchTerm: str = Query(None) # search query, default is None
    ):
    try:
        return taskDAO.getTasksPagination(db, page, pageSize, searchTerm)
    except HTTPException as e:
        raise e

@router.get("/{id}", response_model=TaskSchema)
def getTaskById(id: int, db: Session = Depends(get_db)):
    try:
        return taskDAO.getTaskById(db, id)
    except HTTPException as e:
        raise e

@router.post("/", response_model=TaskSchema, response_model_exclude_none=True)
def createTask(task: TaskCreateSchema, db: Session = Depends(get_db)):
    # Validate Priority
    if task.Priority is not None and task.Priority not in PriorityEnum.__members__.values():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority: {task.Priority}. Must be one of [Low, Medium, High]."
        )

    try:
        return taskDAO.createTask(db, task.Title, task.DueDate, task.Priority, task.IdProject)
    except HTTPException as e:
        raise e

@router.put("/{id}", response_model=TaskSchema, response_model_exclude_none=True)
def updateTask(id: int, task: TaskUpdateSchema, db: Session = Depends(get_db)):
    # Validate Priority
    if task.Priority and task.Priority not in PriorityEnum.__members__.values():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority: {task.Priority}. Must be one of [Low, Medium, High]."
        )
    # Validate Status
    if task.Status and task.Status not in StatusEnum.__members__.values():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: {task.Status}. Must be one of [Pending, In Progress, Completed, Blocked]."
        )

    try:
        return taskDAO.updateTask(db, id, task.Title, task.Status, task.DueDate, task.Priority, task.IdProject)
    except HTTPException as e:
        raise e

@router.delete("/{id}")
def deleteTask(id: int, db: Session = Depends(get_db)):
    try:
        return taskDAO.deleteTask(db, id)
    except HTTPException as e:
        raise e