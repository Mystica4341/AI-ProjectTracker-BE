from pydantic import BaseModel
from enum import Enum
from typing import Optional

class TodoSchema(BaseModel):
  IdTodo: int
  ProjectName: str
  IdProjectMember: int
  Fullname: str
  Email: str
  IdTask: int
  Title: str
  Status: str
  DueDate: str
  Priority: str

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