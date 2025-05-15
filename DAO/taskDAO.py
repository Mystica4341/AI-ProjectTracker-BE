from sqlalchemy.orm import Session
from models.task import Task
from models.project import Project
from DAO import projectDAO, notificationDAO
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

  # get total pages
  totalPages = (totalCount + pageSize - 1) // pageSize

  # append and format data
  for t in tasks:
    project = projectDAO.getProjectById(db, t.IdProject)
    
    t.ProjectName = project.ProjectName

  return {
          "page": page,
          "pageSize": pageSize,
          "totalCount": totalCount,
          "totalPages": totalPages,
          "data": tasks
        }


def getTaskById(db: Session, id: int):
  task = db.query(Task).filter(Task.IdTask == id).first()
  if task is None:
    raise HTTPException(status_code=404, detail="Task not found")

  try:
    project = projectDAO.getProjectById(db, task.IdProject)
  except HTTPException as e:
    raise e

  # append data
  task.ProjectName = project.ProjectName

  return task

def createTask(db: Session, title: str, dueDate: str, priority: str, idProject: int):
  try:
    # check if project exists
    existProject(db, idProject)
  except HTTPException as e:
    raise e
  task = Task(Title=title, DueDate=dueDate, Priority=priority, IdProject=idProject)
  db.add(task)
  db.commit()
  db.refresh(task)
  return task

def updateTask(db: Session, id: int, title: str, status: str, dueDate: str, priority: str, idProject: int):
  try:
    existProject(db, idProject)
    task = getTaskById(db, id)
    if task.Status != status: # if project is changed, notify the new project
      notificationDAO.notifyTaskUpdate(db, id, status)
  except HTTPException as e:
    raise e
  task.Title = title
  task.Status = status
  # task.DateCreate = dateCreate
  task.DueDate = dueDate
  task.Priority = priority
  task.IdProject = idProject
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