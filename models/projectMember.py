from sqlalchemy import Column, Integer, String, Enum
from database import Base

class ProjectMember(Base):
  __tablename__ = "ProjectMember"
  
  IdProjectMember = Column(Integer, primary_key=True, index=True)
  IdUser = Column(Integer)
  UserRole = Column(String)
  IdProject = Column(Integer)