from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO import userDAO
from authentication import authorize
# import Schema
from schemas.userSchema import UserCreateSchema, UserUpdateSchema, UserSchema, UserPagination, RoleEnum

router = APIRouter()

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()

@router.get("/", response_model=UserPagination)
def getUsersPagination(
  db: Session = Depends(get_db),
  page: int = Query(1, ge=1), # page number, default is 1 and must be greater than 1
  pageSize: int = Query(10, ge=1, le= 100), # limit of items per page, default is 10 and must be between 1 and 100
  searchTerm: str = Query(None), # search query, default is None
  user: dict = Depends(authorize("Admin")),
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
  if user.Role and user.Role not in RoleEnum.__members__.values():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: {user.Role}. Must be one of [Super Admin, Admin, User]."
        )
  try:
    return userDAO.createUser(db, user.Username, user.Fullname, user.Email, user.Password, user.PhoneNumber, user.Role, user.Permission)
  except HTTPException as e:
    raise e

@router.put("/{id}", response_model=UserSchema)
def updateUser(id: int, user: UserUpdateSchema , db: Session = Depends(get_db)):
  if user.Role and user.Role not in RoleEnum.__members__.values():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: {user.Role}. Must be one of [Super Admin, Admin, User]."
        )
  try:
    return userDAO.updateUser(db, id, user.Username, user.Username, user.Email, user.Password, user.PhoneNumber, user.Role, user.Permission)
  except HTTPException as e:
    raise e
  
@router.put("/password/{id}", response_model=UserSchema)
def updateUserPassword(id: int, password: str, db: Session = Depends(get_db)):
  try:
    return userDAO.updateUserPassword(db, id, password)
  except HTTPException as e:
    raise e
  
@router.put("/image/{id}", response_model=UserSchema)
def updateUserImage(id: int, image: str, db: Session = Depends(get_db)):
  try:
    return userDAO.updateProfileImage(db, id, image)
  except HTTPException as e:
    raise e

@router.delete("/{id}")
def deleteUser(id: int, db: Session = Depends(get_db)):
  try:
    return userDAO.deleteUser(db, id)
  except HTTPException as e:
    raise e