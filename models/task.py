from sqlalchemy import Column, Integer, String, Enum
from database import Base
from datetime import date

class Task(Base):
    __tablename__ = "Tasks"

    IdTask = Column(Integer, primary_key=True, index=True)
    Title = Column(String)
    Status = Column(Enum("Pending", "In Progress", "Completed", "Blocked"), default="Pending")
    DateCreate = Column(String, default=lambda: date.today().strftime("%d/%m/%Y"))
    DueDate = Column(String)
    Priority = Column(Enum("Low", "Medium", "High"), default="Medium")
    IdProject = Column(Integer)