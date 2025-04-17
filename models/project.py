from sqlalchemy import Column, Integer, String, Date, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import date

class Project(Base):
  __tablename__ = "Projects"

  IdProject = Column(Integer, primary_key=True, index=True)
  ProjectName = Column(String)
  DateCreate = Column(String, default=lambda: date.today().strftime("%d/%m/%Y"))
  Manager = Column(String)
  Status = Column(Enum("Active", "Completed", "On Hold", "Cancelled"), default="Active")
  Priority = Column(Enum("Low", "Medium", "High"), default="Medium")

  @property
  def manager(self):
    return User.query.get(self.Manager)

  @property
  def formattedDate(self):
    return self.DateCreate