from pydantic import BaseModel
from typing import Optional

class ProjectMemberSchema(BaseModel):
  IdProjectMember: int
  IdUser: int
  UserRole: str
  Fullname: Optional[str] = None
  Email: Optional[str] = None
  IdProject: int
  ProjectName: Optional[str] = None

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

class ProjectMemberPaginationSchema(BaseModel):
  page: int
  pageSize: int
  totalCount: int
  totalPages: int
  data: list[ProjectMemberSchema]
  
  class Config:
    orm_mode = True