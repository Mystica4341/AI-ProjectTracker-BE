from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ProjectStorageSchema(BaseModel):
  IdProjectStorage: int
  IdProject: int
  ProjectName: Optional[str] = None
  StorageURL: str
  Filename: str
  Size: int
  uploadDate: str

  class Config:
    orm_mode = True

class ProjectStorageCreateSchema(BaseModel):
  IdProject: int
  StorageURL: str
  Filename: str
  Size: int

  class Config:
    orm_mode = True

class ProjectStorageUpdateSchema(BaseModel):
  IdProject: int
  StorageURL: str
  Filename: str
  Size: int
  uploadDate: str

  class Config:
    orm_mode = True

class ProjectStoragePaginationSchema(BaseModel):
  page: int
  pageSize: int
  totalCount: int
  totalPages: int
  data: list[ProjectStorageSchema]
  
  class Config:
    orm_mode = True


