from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship
# from models.user import User
# from models.project import Project

class ProjectMember(Base):
  __tablename__ = "ProjectMembers"
  
  IdProjectMember = Column(Integer, primary_key=True, index=True)
  IdUser = Column(Integer)
  UserRole = Column(String)
  IdProject = Column(Integer)