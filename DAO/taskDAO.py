from sqlalchemy.orm import Session
from models.task import Task
from models.project import Project
from DAO import projectDAO
from fastapi import HTTPException

def getTasksPagination(db: Session, page: int, pageSize: int, searchTerm: str = None):
  query = db.query(Task)

  # filter by search term
  if searchTerm:
    query = db.query(Task).filter(Task.Title.ilike(f"%{searchTerm}%") | Task.Status.ilike(f"%{searchTerm}%") | Task.Priority.ilike(f"%{searchTerm}%"))

  # sorting
  query = query.order_by(Task.IdTask.asc())

  # pagination
  tasks = query.offset((page - 1) * pageSize).limit(pageSize).all()

  # get total count
  totalCount = db.query(Task).count()

  # append and format data
  results = [
      {
        "IdTask": task.IdTask,
        "Title": task.Title,
        "Status": task.Status,
        "DueDate": task.DueDate,
        "Priority": task.Priority,
        "IdProject": task.IdProject,
        "ProjectName": db.query(Project).filter(Project.IdProject == task.IdProject).first().ProjectName
      }
      for task in tasks
  ]

  return {
          "page": page,
          "pageSize": pageSize,
          "totalCount": totalCount,
          "data": results
        }


def getTaskById(db: Session, id: int):
  task = db.query(Task).filter(Task.IdTask == id).first()
  if task is None:
    raise HTTPException(status_code=404, detail="Task not found")

  try:
    project = projectDAO.getProjectById(db, task.IdProject)
  except HTTPException as e:
    raise e

  # Attach additional fields to the ORM object (if needed)
  task.ProjectName = project.ProjectName

  return task
  
  # return {
  #   "IdTask": task.IdTask,
  #   "Title": task.Title,
  #   "Status": task.Status,
  #   "DueDate": task.DueDate,
  #   "Priority": task.Priority,
  #   "IdProject": task.IdProject,
  #   "ProjectName": project.ProjectName
  # }

def createTask(db: Session, title: str, due_date: str, priority: str, id_project: int):
  try:
    # check if project exists
    existProject(db, id_project)
  except HTTPException as e:
    raise e
  task = Task(Title=title, DueDate=due_date, Priority=priority, IdProject=id_project)
  db.add(task)
  db.commit()
  db.refresh(task)
  return task

def updateTask(db: Session, id: int, title: str, status: str, due_date: str, priority: str, id_project: int):
  try:
    existProject(db, id_project)
    task = getTaskById(db, id)
  except HTTPException as e:
    raise e
  task.Title = title
  task.Status = status
  task.DueDate = due_date
  task.Priority = priority
  task.IdProject = id_project
  db.commit()
  db.refresh(task)
  return task

def deleteTask(db: Session, id: int):
  try:
    task = getTaskById(db, id)
  except HTTPException as e:
    raise e
  db.delete(task)
  db.commit()
  return {"detail": "Task deleted successfully"}

def existProject(db: Session, id: int):
  project = db.query(Project).filter(Project.IdProject == id).first()
  if project is None:
    raise HTTPException(status_code=404, detail="There is no project with id: " + str(id))
  return project