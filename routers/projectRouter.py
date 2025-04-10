from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from datetime import datetime
from DAO import projectDAO
#import Schema
from schemas.projectSchema import ProjectSchema, ProjectUpdateSchema, ProjectCreateSchema, StatusEnum, PriorityEnum

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all projects
@router.get("/", response_model=list[ProjectSchema])
def getAllProjects(db: Session = Depends(get_db)):
    return projectDAO.getAllProjects(db)

# Get project by id
@router.get("/{id}", response_model=ProjectSchema)
def getProjectById(id: int, db: Session = Depends(get_db)):
    try:
      return projectDAO.getProjectById(db, id)
    except HTTPException as e:
      raise e

# Create project
@router.post("/", response_model=ProjectSchema)
def createProject(project: ProjectCreateSchema, db: Session = Depends(get_db)):
    try:
      return projectDAO.createProject(db, project.ProjectName, None, None, None, None)
    except HTTPException as e:
      raise e  

# Update project
@router.put("/{id}", response_model=ProjectSchema)  
def updateProject(id: int, project: ProjectUpdateSchema, db: Session = Depends(get_db)):
        # Validate Status
    if project.Status and project.Status not in StatusEnum.__members__.values():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: {project.Status}. Must be one of [Active, Completed, On Hold, Cancelled]."
        )
    # Validate Priority
    if project.Priority and project.Priority not in PriorityEnum.__members__.values():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority: {project.Priority}. Must be one of [Low, Medium, High]."
        )
    try:  
      return projectDAO.updateProject(db, id, project.ProjectName, None, project.Manager, project.Status, project.Priority)  
    except HTTPException as e:  
      raise e  

# Delete project  
@router.delete("/{id}")  
def deleteProject(id: int, db: Session = Depends(get_db)):  
    try:  
      return projectDAO.deleteProject(db, id)
    except HTTPException as e:  
      raise e