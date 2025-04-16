from sqlalchemy.orm import Session
from models.project import Project
from fastapi import HTTPException


def getProjectPagination(db: Session, page: int, pageSize: int, searchTerm: str = None):
  query = db.query(Project)
  # filter by search term
  if searchTerm:
    query = db.query(Project).filter(Project.ProjectName == searchTerm or Project.Status == searchTerm or Project.Priority == searchTerm)
  # sorting
  query = query.order_by(Project.IdProject.asc())
  # pagination
  projects = query.offset((page - 1) * pageSize).limit(pageSize).all()
  # get total count
  totalCount = db.query(Project).count()
  return projects, totalCount

def getProjectById(db: Session, id: int):
  project = db.query(Project).filter(Project.IdProject == id).first()
  if not project:
    raise HTTPException(status_code=404, detail="Project not found")
  return project

def createProject(db: Session, ProjectName: str, DateCreate: str, Manager: int, Status: str, Priority: str):
  project = Project(ProjectName=ProjectName, DateCreate=DateCreate, Manager=Manager, Status=Status, Priority=Priority)
  db.add(project)
  db.commit()
  db.refresh(project)
  return project

def updateProject(db: Session, id: int, ProjectName: str, DateCreate: str, Manager: int, Status: str, Priority: str):
  try:
    project = getProjectById(db, id)
  except HTTPException as e:
    raise e
  project.ProjectName = ProjectName
  # project.DateCreate = DateCreate
  project.Manager = Manager
  project.Status = Status
  project.Priority = Priority
  db.add(project)
  db.commit()
  db.refresh(project)
  return project

def deleteProject(db: Session, id: int):
  try:
    project = getProjectById(db, id)
  except HTTPException as e:
    raise e
  db.delete(project)
  db.commit()
  return {"detail": "Project deleted successfully"}

  