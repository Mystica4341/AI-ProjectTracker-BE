from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO import userDAO
# import Schema
from schemas.userSchema import UserCreateSchema, UserUpdateSchema, UserSchema

router = APIRouter()

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()

@router.get("/")
def getUsersPagination(
  db: Session = Depends(get_db),
  page: int = Query(1, ge=1), # page number, default is 1 and must be greater than 1
  pageSize: int = Query(10, ge=1, le= 100), # limit of items per page, default is 10 and must be between 1 and 100
  searchTerm: str = Query(None) # search query, default is None
  ):
  try:
    return userDAO.getUsersPagination(db, page, pageSize, searchTerm)
  except HTTPException as e:
    raise e

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