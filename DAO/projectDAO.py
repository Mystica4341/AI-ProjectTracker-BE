from sqlalchemy.orm import Session
from models.project import Project
from fastapi import HTTPException
from AI import aiRouter
from DAO import notificationDAO

def getProjectsPagination(db: Session, page: int, pageSize: int, searchTerm: str = None):
  query = db.query(Project)

  # filter by search term
  if searchTerm:
    query = query.filter(Project.ProjectName.ilike(f"%{searchTerm}%") | Project.Status.ilike(f"%{searchTerm}%") | Project.Priority.ilike(f"%{searchTerm}%"))

  # sorting
  query = query.order_by(Project.IdProject.asc())

  # pagination
  projects = query.offset((page - 1) * pageSize).limit(pageSize).all()

  # get total count
  totalCount = db.query(Project).count()

  # get total pages
  totalPages = (totalCount + pageSize - 1) // pageSize

  return {
          "page": page,
          "pageSize": pageSize,
          "totalCount": totalCount,
          "totalPages": totalPages,
          "data": projects
        }

def getProjectById(db: Session, id: int):
  project = db.query(Project).filter(Project.IdProject == id).first()
  if not project:
    raise HTTPException(status_code=404, detail="Project not found")
  return project

def createProject(db: Session, projectName: str, manager: int, status: str, priority: str):
  project = Project(ProjectName=projectName, Manager=manager, Status=status, Priority=priority)
  db.add(project)
  db.commit()
  db.refresh(project)
  aiRouter.createQdrant(project.IdProject)
  return project

def updateProject(db: Session, id: int, projectName: str, dateCreate: str, manager: int, status: str, priority: str):
  try:
    project = getProjectById(db, id)
  except HTTPException as e:
    raise e
  project.ProjectName = projectName
  # project.DateCreate = dateCreate
  project.Manager = manager
  project.Status = status
  project.Priority = priority
  db.add(project)
  db.commit()
  db.refresh(project)
  
  if project.Manager != manager: # if manager is changed, notify the new manager
    notificationDAO.notifyManagerAssignedToProject(db, manager, project.IdProject)
  
  return project

def deleteProject(db: Session, id: int):
  try:
    project = getProjectById(db, id)
  except HTTPException as e:
    raise e
  db.delete(project)
  db.commit()
  return {"detail": "Project deleted successfully"}

  