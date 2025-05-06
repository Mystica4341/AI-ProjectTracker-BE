from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO import projectStorageDAO
from authentication import authorize
# import Schema
from schemas.projectStorageSchema import ProjectStorageSchema, ProjectStorageCreateSchema, ProjectStorageUpdateSchema, ProjectStoragePaginationSchema

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=ProjectStoragePaginationSchema)
def getProjectStoragesPagination(
  db: Session = Depends(get_db),
  page: int = Query(1, gt=0),
  pageSize: int = Query(10, gt=0),
  searchTerm: str = Query(None),
  user: dict = Depends(authorize("Admin"))
):
  try:
    return projectStorageDAO.getProjectStoragesPagination(db, page, pageSize, searchTerm)
  except HTTPException as e:
    raise e

@router.get("/{id}", response_model=ProjectStorageSchema)
def getProjectStorageByIdProject(id: int, db: Session = Depends(get_db)):
  try:
    return projectStorageDAO.getProjectStorageByIdProject(db, id)
  except HTTPException as e:
    raise e

@router.post("/", response_model=ProjectStorageSchema)
def createProjectStorage(projectStorage: ProjectStorageCreateSchema, db: Session = Depends(get_db)):
  try:
    return projectStorageDAO.createProjectStorage(db, projectStorage.IdProject, projectStorage.StorageURL, projectStorage.Filename, projectStorage.Size, projectStorage.uploadDate)
  except HTTPException as e:
    raise e

@router.put("/{id}", response_model=ProjectStorageSchema)
def updateProjectStorage(id: int, projectStorage: ProjectStorageUpdateSchema, db: Session = Depends(get_db)):
  try:
    return projectStorageDAO.updateProjectStorage(db, id, projectStorage.IdProject, projectStorage.StorageURL, projectStorage.Filename, projectStorage.Size, projectStorage.uploadDate)
  except HTTPException as e:
    raise e

@router.delete("/{id}")
def deleteProjectStorage(id: int, db: Session = Depends(get_db)):
  try:
    return projectStorageDAO.deleteProjectStorage(db, id)
  except HTTPException as e:
    raise e
