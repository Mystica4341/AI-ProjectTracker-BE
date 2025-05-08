from pydantic import BaseModel
from enum import Enum
from typing import Optional, List

class UserPermissionSchema(BaseModel):
    IdUser: Optional[int]
    Username: Optional[str]
    Email: Optional[str]
    IdPermission: Optional[int]
    PermissionName: Optional[str]

    class Config:
        orm_mode = True
        
class UserPermissionUpdateSchema(BaseModel):
    IdUser: Optional[int]
    IdPermission: Optional[int]

    class Config:
        orm_mode = True
        
class UserPermissionCreateSchema(BaseModel):
    IdUser: Optional[int]
    PermissionList: List[str]

    class Config:
        orm_mode = True
        
class UserPermissionDeleteSchema(BaseModel):
    IdUser: Optional[int]
    PermissionList: List[str]
    
    class Config:
        orm_mode = True

class UserPermissionPagination(BaseModel):
    page: int
    pageSize: int
    totalCount: int
    totalPages: int
    data: list[UserPermissionSchema]

    class Config:
        orm_mode = True