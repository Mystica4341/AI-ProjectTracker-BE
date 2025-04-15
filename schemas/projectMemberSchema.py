from pydantic import BaseModel
from typing import Optional

class ProjectMemberSchema(BaseModel):
  IdProjectMember: int
  IdProject: int
  IdUser: int
  UserRole: str
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
  data: list[ProjectMemberSchema]
  class Config:
    orm_mode = True