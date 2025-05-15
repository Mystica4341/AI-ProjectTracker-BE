from sqlalchemy.orm import Session
from models.projectMember import ProjectMember
from models.project import Project
from models.user import User
from DAO import userDAO, projectDAO, notificationDAO
from fastapi import HTTPException

def getProjectMembersPagination(db: Session, page: int, pageSize: int, searchTerm: str = None):
  query = db.query(ProjectMember).join(Project, ProjectMember.IdProject == Project.IdProject).join(User, ProjectMember.IdUser == User.IdUser)

  # filter by search term
  if searchTerm:
    query = query.filter(ProjectMember.UserRole.ilike(f"%{searchTerm}%") | 
                         Project.ProjectName.ilike(f"%{searchTerm}%") | 
                         User.Fullname.ilike(f"%{searchTerm}%") | User.Email.ilike(f"%{searchTerm}%"))

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
    project = projectDAO.getProjectById(db, projectMember.IdProject)
    user = userDAO.getUserById(db, projectMember.IdUser)
  except HTTPException as e:
    raise e
  
  projectMember.Fullname = user.Fullname
  projectMember.Email = user.Email
  projectMember.ProjectName = project.ProjectName

  return projectMember

def getProjectMemberByIdProject(db: Session, id: int):
  projectMember = db.query(ProjectMember).filter(ProjectMember.IdProject == id).all()
  if projectMember is None:
    raise HTTPException(status_code=404, detail="Project member not found")

  for member in projectMember:
    project = projectDAO.getProjectById(db, member.IdProject)
    user = userDAO.getUserById(db, member.IdUser)
    
    member.Fullname = user.Fullname
    member.Email = user.Email
    member.ProjectName = project.ProjectName

  return projectMember

def createProjectMember(db: Session, idUser: int, userRole: str, idProject: int):
  try:
    # check if project exists
    existProject(db, idProject)
    # check if user exists
    existUser(db, idUser)
    # check if there is project member already exists
    duplicateProjectMember(db, idUser, idProject)
  except HTTPException as e:
    raise e
    
  projectMember = ProjectMember(IdUser=idUser, UserRole=userRole, IdProject=idProject)
  db.add(projectMember)
  db.commit()
  db.refresh(projectMember)
  
  # Notify the user
  notificationDAO.notifyAddedProjectMember(db, idProject, idUser, userRole)
  
  return projectMember

def updateProjectMember(db: Session, id: int, idUser: int, userRole: str, idProject: int):
  try:
    # check if project exists
    existProject(db, idProject)
    # check if user exists
    existUser(db, idUser)
    # check if there is project member already exists
    # duplicateProjectMember(db, IdUser, IdProject)
    # find project member by Id
    projectMember = getProjectMemberById(db, id)
  except HTTPException as e:
    raise e

  projectMember.IdUser = idUser
  projectMember.UserRole = userRole
  projectMember.IdProject = idProject
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
  
  # Notify the user
  notificationDAO.notifyRemovedProjectMember(db, projectMember.IdProject, projectMember.IdUser)
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

def duplicateProjectMember(db: Session, idUser: int, idProject: int):
  projectMember = db.query(ProjectMember).filter(ProjectMember.IdUser == idUser, ProjectMember.IdProject == idProject).first()
  if projectMember is not None:
    raise HTTPException(status_code=400, detail="This user is already a member of this project")
