from sqlalchemy import Column, Integer, String
from datetime import datetime
from database import Base

class ProjectStorage(Base):
    __tablename__ = "ProjectStorage"

    IdStorage = Column(Integer, primary_key=True, index=True)
    IdProject = Column(Integer)
    StorageUrl = Column(String)
    Filename = Column(String)
    Size = Column(Integer)
    uploadDate = Column(String, default=lambda: datetime.now().strftime("%d/%m/%Y %H:%M"))
    