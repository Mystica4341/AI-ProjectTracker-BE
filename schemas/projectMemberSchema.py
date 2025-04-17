from pydantic import BaseModel
from typing import Optional

class ProjectMemberSchema(BaseModel):
  IdProjectMember: int
  IdUser: int
  UserRole: str
  Fullname: Optional[str]
  Email: Optional[str]
  IdProject: int
  ProjectName: Optional[str]

  class Config:
    orm_mode = True

class ProjectMemberCreateSchema(BaseModel):
  IdProject: int
  IdUser: int
  UserRole: str

  class Config:
    orm_mode = True

class ProjectMemberUpdateSchema(BaseModel):
  IdProject: int
  IdUser: int
  UserRole: str
  
  class Config:
    orm_mode = True