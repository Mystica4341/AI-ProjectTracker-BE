from sqlalchemy.orm import Session
from models.projectStorage import ProjectStorage
from fastapi import HTTPException
from models.project import Project
from DAO import projectDAO

def getProjectStoragePaginated(db: Session, page: int, pageSize: int, searchTerm: str = None):
  query = db.query(ProjectStorage).join(Project, ProjectStorage.IdProject == Project.IdProject)

  # filter by search term
  if searchTerm:
    query = query.filter(ProjectStorage.StorageUrl.ilike(f"%{searchTerm}%") | 
                         ProjectStorage.Filename.ilike(f"%{searchTerm}%") | 
                         Project.ProjectName.ilike(f"%{searchTerm}%"))

  # sorting
  query = query.order_by(ProjectStorage.IdStorage.asc())

  # pagination
  projectStorages = query.offset((page - 1) * pageSize).limit(pageSize).all()

  # get total count
  totalCount = db.query(ProjectStorage).count()

  # get total pages
  totalPages = (totalCount + pageSize - 1) // pageSize

  # append and format data
  for projectStorage in projectStorages:
    project = projectDAO.getProjectById(db, projectStorage.IdProject)
    
    projectStorage.ProjectName = project.ProjectName

  return {
          "page": page,
          "pageSize": pageSize,
          "totalCount": totalCount,
          "totalPages": totalPages,
          "data": projectStorages
        }

def getProjectStorageByIdProject(db: Session, id: int):
  projectStorage = db.query(ProjectStorage).filter(ProjectStorage.IdProject == id).first()
  if not projectStorage:
    raise HTTPException(status_code=404, detail="Id Project not found")
  return projectStorage

def createProjectStorage(db: Session, idProject: int, storageUrl: str, filename: str, Size: int, uploadDate: str):
  try:
    # check if project exists
    existProject(db, idProject)
  except HTTPException as e:
    raise e

  projectStorage = ProjectStorage(IdProject=idProject, StorageUrl=storageUrl, Filename=filename, Size=Size, uploadDate=uploadDate)
  db.add(projectStorage)
  db.commit()
  db.refresh(projectStorage)
  return projectStorage

def updateProjectStorage(db: Session, id: int, idProject: int, storageUrl: str, filename: str, Size: int, uploadDate: str):
  try:
    # check if project exists
    existProject(db, idProject)
    # find project storage by Id
    projectStorage = getProjectStorageByIdProject(db, id)
  except HTTPException as e:
    raise e

  projectStorage.IdProject = idProject
  projectStorage.StorageUrl = storageUrl
  projectStorage.Filename = filename
  projectStorage.Size = Size
  projectStorage.uploadDate = uploadDate
  db.commit()
  db.refresh(projectStorage)
  return projectStorage

def deleteProjectStorage(db: Session, id: int):
  try:
    projectStorage = getProjectStorageByIdProject(db, id)
  except HTTPException as e:
    raise e
  db.delete(projectStorage)
  db.commit()
  return {"detail": "Project storage deleted successfully"}

def existProject(db: Session, id: int):
  project = db.query(Project).filter(Project.IdProject == id).first()
  if project is None:
    raise HTTPException(status_code=404, detail="There is no project with id: " + str(id))
  return project
