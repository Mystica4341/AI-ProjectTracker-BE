from pydantic import BaseModel, validator
from enum import Enum
from typing import Optional
from datetime import datetime

# Define the Project schema and add config for ORM
class ProjectSchema(BaseModel):
    IdProject: int
    ProjectName: str
    DateCreate: Optional[str] = None
    Manager: Optional[int] = None
    Status: Optional[str] = None
    Priority: Optional[str] = None

    @validator("DateCreate", pre=True)
    def format_date(cls, value):
        if isinstance(value, datetime):
            return value.strftime("%d/%m/%Y")
        return value

    class Config:
        orm_mode = True

class ProjectUpdateSchema(BaseModel):
    ProjectName: str
    Manager: Optional[int] = None
    Status: Optional[str] = None
    Priority: Optional[str] = None

    class Config:
        orm_mode = True

class ProjectCreateSchema(BaseModel):
    ProjectName: str

    class Config:
        orm_mode = True

# Define enums for validation
class StatusEnum(str, Enum):
    Active = "Active"
    Completed = "Completed"
    OnHold = "On Hold"
    Cancelled = "Cancelled"

class PriorityEnum(str, Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"