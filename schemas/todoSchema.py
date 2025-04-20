from pydantic import BaseModel
from enum import Enum
from typing import Optional

class TodoSchema(BaseModel):
  IdTodo: int
  ProjectName: Optional[str] = None
  IdProjectMember: int
  Fullname: Optional[str] = None
  Email: Optional[str] = None
  IdTask: int
  Title: Optional[str] = None
  Status: Optional[str] = None
  DueDate: Optional[str] = None
  Priority: Optional[str] = None

  class Config:
    orm_mode = True

class TodoUpdateSchema(BaseModel):
  IdProjectMember: int
  IdTask: int

  class Config:
    orm_mode = True

class TodoCreateSchema(BaseModel):
  IdProjectMember: int
  IdTask: int

  class Config:
    orm_mode = True