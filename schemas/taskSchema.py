from pydantic import BaseModel
from typing import Optional
from enum import Enum

class TaskSchema(BaseModel):
  IdTask: int
  Title: str
  Status: Optional[str]
  DateCreate: Optional[str]
  DueDate: Optional[str]
  Priority: Optional[str]
  IdProject: Optional[int]
  ProjectName: Optional[str] = None

  class Config:
    orm_mode = True

class TaskCreateSchema(BaseModel):
  Title: str
  DateCreate: Optional[str]
  DueDate: Optional[str]
  Priority: Optional[str] = "Medium"
  IdProject: Optional[int]

  class Config:
    orm_mode = True

class TaskUpdateSchema(BaseModel):
  Title: str
  Status: Optional[str]
  DateCreate: Optional[str]
  DueDate: Optional[str]
  Priority: Optional[str]
  IdProject: Optional[int]
  
  class Config:
    orm_mode = True

# Define enums for validation
class StatusEnum(str, Enum):
  Pending = "Pending"
  InProgress = "In Progress"
  Completed = "Completed"
  Blocked = "Blocked"

class PriorityEnum(str, Enum):
  Low = "Low"
  Medium = "Medium"
  High = "High"

class TaskPaginationSchema(BaseModel):
  page: int
  pageSize: int
  totalCount: int
  totalPages: int
  data: list[TaskSchema]

  class Config:
    orm_mode = True