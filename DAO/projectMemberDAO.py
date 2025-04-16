from sqlalchemy.orm import Session
from models.projectMember import ProjectMember
from models.project import Project
from models.user import User
from fastapi import HTTPException

def getProjectMembersPagination(db: Session, page: int, pageSize: int, searchTerm: str = None):
  query = db.query(ProjectMember)
  # filter by search term
  if searchTerm:
    query = db.query(ProjectMember).filter(ProjectMember.UserRole == searchTerm)
  # sorting
  query = query.order_by(ProjectMember.UserRole.asc())
  # pagination
  projectMembers = query.offset((page - 1) * pageSize).limit(pageSize).all()
  # get total count
  totalCount = db.query(ProjectMember).count()
  return projectMembers, totalCount

def getProjectMemberById(db: Session, id: int):
  projectMember = db.query(ProjectMember).filter(ProjectMember.IdProjectMember == id).first()
  if projectMember is None:
    raise HTTPException(status_code=404, detail="Project member not found")
  return projectMember

def createProjectMember(db: Session, IdUser: int, UserRole: str, IdProject: int):
  try:
    # check if project exists
    existProject(db, IdProject)
    # check if user exists
    existUser(db, IdUser)
    # check if there is project member already exists
    duplicateProjectMember(db, IdUser, IdProject)
  except HTTPException as e:
    raise e
    
  projectMember = ProjectMember(IdUser=IdUser, UserRole=UserRole, IdProject=IdProject)
  db.add(projectMember)
  db.commit()
  db.refresh(projectMember)
  return projectMember

def updateProjectMember(db: Session, id: int, IdUser: int, UserRole: str, IdProject: int):
  try:
    # check if project exists
    existProject(db, IdProject)
    # check if user exists
    existUser(db, IdUser)
    # check if there is project member already exists
    duplicateProjectMember(db, IdUser, IdProject)
    # find project member by Id
    projectMember = getProjectMemberById(db, id)
  except HTTPException as e:
    raise e

  projectMember.IdUser = IdUser
  projectMember.UserRole = UserRole
  projectMember.IdProject = IdProject
  db.commit()
  db.refresh(projectMember)
  return projectMember

def deleteProjectMember(db: Session, id: int):
  try:
    projectMember = getProjectMemberById(db, id)
  except HTTPException as e:
    raise e
  db.delete(projectMember)
  db.commit()
  return {"detail": "Project member deleted successfully"}

def existProject(db: Session, id: int):
  project = db.query(Project).filter(Project.IdProject == id).first()
  if project is None:
    raise HTTPException(status_code=404, detail="There is no project with id: " + str(id))
  return project

def existUser(db: Session, id: int):
  user = db.query(User).filter(User.IdUser == id).first()
  if user is None:
    raise HTTPException(status_code=404, detail="There is no user with id: " + str(id))
  return user

def duplicateProjectMember(db: Session, IdUser: int, IdProject: int):
  projectMember = db.query(ProjectMember).filter(ProjectMember.IdUser == IdUser, ProjectMember.IdProject == IdProject).first()
  if projectMember is not None:
    raise HTTPException(status_code=400, detail="This user is already a member of this project")
  return projectMember
