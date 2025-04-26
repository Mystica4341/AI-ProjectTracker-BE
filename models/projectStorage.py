from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class ProjectStorage(Base):
    __tablename__ = "ProjectStorage"

    IdStorage = Column(Integer, primary_key=True, index=True)
    IdProject = Column(Integer)
    StorageUrl = Column(String)