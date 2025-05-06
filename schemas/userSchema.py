from pydantic import BaseModel
from enum import Enum
from typing import Optional

# Define the User schema and add config for ORM
class UserSchema(BaseModel):
    IdUser: int
    Username: str
    Fullname: str
    Email: str
    Password: Optional[str]
    PhoneNumber: str
    Role: Optional[str]
    Permission: Optional[str]

    class Config:
        orm_mode = True

class UserUpdateSchema(BaseModel):
    Username: str
    Fullname: str
    Email: str
    Password: Optional[str]
    PhoneNumber: str
    Role: Optional[str]
    Permission: Optional[str]

    class Config:
        orm_mode = True

class UserCreateSchema(BaseModel):
    Username: str
    Fullname: str
    Email: str
    Password: Optional[str] = "Pa$$w0rd"
    PhoneNumber: str
    Role: Optional[str] = ""
    Permission: Optional[str] = "none"

    class Config:
        orm_mode = True

class UserLoginSchema(BaseModel):
    Username: str
    Password: str
    
    class Config:
        orm_mode = True
        
class RoleEnum(str, Enum):
    SuperAdmin = "Super Admin"
    Admin = "Admin"
    User = "User"

class UserPagination(BaseModel):
    page: int
    pageSize: int
    totalCount: int
    totalPages: int
    data: list[UserSchema]

    class Config:
        orm_mode = True
