from sqlalchemy import Column, Integer, String, Enum
from database import Base

class Task(Base):
    __tablename__ = "Task"

    IdTask = Column(Integer, primary_key=True, index=True)
    Title = Column(String)
    Status = Column(Enum("Pending", "In Progress", "Completed", "Blocked"), default="Pending")
    DueDate = Column(String)
    Priority = Column(Enum("Low", "Medium", "High"), default="Medium")
    IdProject = Column(Integer)