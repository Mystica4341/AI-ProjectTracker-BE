from fastapi import APIRouter, Depends, HTTPException, Query 
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO import projectMemberDAO
from schemas.projectMemberSchema import ProjectMemberSchema, ProjectMemberCreateSchema, ProjectMemberUpdateSchema

router = APIRouter()

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()

@router.get("/")
def getProjectMembersPagination(
  db: Session = Depends(get_db),
  page: int = Query(1, ge=1), # page number, default is 1 and must be greater than 1
  pageSize: int = Query(10, ge=1, le= 100), # limit of items per page, default is 10 and must be between 1 and 100
  searchTerm: str = Query(None) # search query, default is None
  ):
  try:
    return projectMemberDAO.getProjectMembersPagination(db, page, pageSize, searchTerm)
  except HTTPException as e:
    raise e

@router.get("/{id}", response_model=ProjectMemberSchema)
def getProjectMemberById(id: int, db: Session = Depends(get_db)):
  try:
    return projectMemberDAO.getProjectMemberById(db, id)
  except HTTPException as e:
    raise e

@router.post("/", response_model=ProjectMemberSchema)
def createProjectMember(projectMember: ProjectMemberCreateSchema, db: Session = Depends(get_db)):
  try:
    return projectMemberDAO.createProjectMember(db, projectMember.IdUser, projectMember.UserRole, projectMember.IdProject)
  except HTTPException as e:
    raise e

@router.put("/{id}", response_model=ProjectMemberSchema)
def updateProjectMember(id: int, projectMember: ProjectMemberUpdateSchema, db: Session = Depends(get_db)):
  try:
    return projectMemberDAO.updateProjectMember(db, id, projectMember.IdUser, projectMember.UserRole, projectMember.IdProject)
  except HTTPException as e:
    raise e

@router.delete("/{id}")
def deleteProjectMember(id: int, db: Session = Depends(get_db)):
  try:
    return projectMemberDAO.deleteProjectMember(db, id)
  except HTTPException as e:
    raise e