from sqlalchemy.orm import Session
from models.projectMember import ProjectMember
from models.project import Project
from models.user import User
from DAO import userDAO, projectDAO
from fastapi import HTTPException

def getAllProjectMembers(db: Session):
  projectMembers = db.query(ProjectMember).all()
  return projectMembers

def getProjectMembersPagination(db: Session, page: int, pageSize: int, searchTerm: str = None):
  query = db.query(ProjectMember)

  # filter by search term
  if searchTerm:
    query = query.filter(ProjectMember.UserRole.ilike(f"%{searchTerm}%"))

  # sorting
  query = query.order_by(ProjectMember.IdProjectMember.asc())

  # pagination
  projectMembers = query.offset((page - 1) * pageSize).limit(pageSize).all()

  # get total count
  totalCount = db.query(ProjectMember).count()

  # get total pages
  totalPages = (totalCount + pageSize - 1) // pageSize

  # append and format data
  for member in projectMembers:
    project = projectDAO.getProjectById(db, member.IdProject)
    user = userDAO.getUserById(db, member.IdUser)
    
    member.Fullname = user.Fullname
    member.Email = user.Email
    member.ProjectName = project.ProjectName

  return {
          "page": page,
          "pageSize": pageSize,
          "totalCount": totalCount,
          "totalPages": totalPages,
          "data": projectMembers
      }

def getProjectMemberById(db: Session, id: int):
  projectMember = db.query(ProjectMember).filter(ProjectMember.IdProjectMember == id).first()
  if projectMember is None:
    raise HTTPException(status_code=404, detail="Project member not found")

  try:
    user = userDAO.getUserById(db, projectMember.IdUser)
    project = projectDAO.getProjectById(db, projectMember.IdProject)
  except HTTPException as e:
    raise e

  # append data
  projectMember.Fullname = user.Fullname
  projectMember.Email = user.Email
  projectMember.ProjectName = project.ProjectName

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
    # duplicateProjectMember(db, IdUser, IdProject)
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
