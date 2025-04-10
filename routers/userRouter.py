from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from pydantic import BaseModel
from DAO import userDAO

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the User schema and add config for ORM
class UserSchema(BaseModel):
    IdUser: int
    Username: str
    Fullname: str
    Email: str
    Password: str
    PhoneNumber: str
    Role: str
    Permission: str
    class Config:
        orm_mode = True

class UserUpdateSchema(BaseModel):
    Username: str
    Fullname: str
    Email: str
    Password: str
    PhoneNumber: str
    Role: str
    Permission: str
    class Config:
        orm_mode = True

class UserCreateSchema(BaseModel):
    Username: str
    Fullname: str
    Email: str
    Password: str
    PhoneNumber: str
    class Config:
        orm_mode = True

@router.get("/", response_model=list[UserSchema])
def getAllUsers(db: Session = Depends(get_db)):
    return userDAO.getAllUsers(db)

@router.get("/{id}", response_model=UserSchema)
def getUserById(id: int, db: Session = Depends(get_db)):
    try:
      return userDAO.getUserById(db, id)
    except HTTPException as e:
      raise e

@router.get("/email/{email}", response_model=UserSchema)
def getUserByEmail(email: str, db: Session = Depends(get_db)):
    try:
      return userDAO.getUserByEmail(db, email)
    except HTTPException as e:
      raise e

@router.get("/username/{username}", response_model=UserSchema)
def getUserByUsername(username: str, db: Session = Depends(get_db)):
    try:
      return userDAO.getUserByUsername(db, username)
    except HTTPException as e:
      raise e

@router.post("/", response_model=UserSchema)
def createUser(user: UserCreateSchema, db: Session = Depends(get_db)):
    try:
      return userDAO.createUser(db, user.Username, user.Username, user.Email, user.Password, user.PhoneNumber)
    except HTTPException as e:
      raise e

@router.put("/{id}", response_model=UserSchema)
def updateUser(id: int, user: UserUpdateSchema , db: Session = Depends(get_db)):
    try:
      return userDAO.updateUser(db, id, user.Username, user.Username, user.Email, user.Password, user.PhoneNumber, user.Role, user.Permission)
    except HTTPException as e:
      raise e

@router.delete("/{id}")
def deleteUser(id: int, db: Session = Depends(get_db)):
    try:
      return userDAO.deleteUser(db, id)
    except HTTPException as e:
      raise e