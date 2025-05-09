from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO import permissionDAO, userPermissionDAO
from authentication import authorize
#import Schema
from schemas.userPermissionSchema import UserPermissionSchema, UserPermissionUpdateSchema, UserPermissionCreateSchema, UserPermissionPagination, UserPermissionDeleteSchema

router = APIRouter()

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()
      
@router.get("/", response_model=UserPermissionPagination)
def getUserPermissionsPagination(
  db: Session = Depends(get_db), 
  page: int = Query(1, ge=1), 
  pageSize: int = Query(10, ge=1, le=100), 
  searchTerm: str = Query(None), 
  user: dict = Depends(authorize(get_db, "GET: UserPermissions")),
  ):
  try:
    return userPermissionDAO.getUserPermissionsPagination(db, page, pageSize, searchTerm)
  except HTTPException as e: 
    raise e
  
@router.get("/{idUser}", response_model=list[UserPermissionSchema])
def getUserPermissionByIdUser(idUser: int, db: Session = Depends(get_db)):
  try:
    return userPermissionDAO.getUserPermissionByIdUser(db, idUser)
  except HTTPException as e: 
    raise e
  
@router.post("/")
def createUserPermission(userPermission: UserPermissionCreateSchema, db: Session = Depends(get_db), user: dict = Depends(authorize(get_db, "POST: UserPermissions"))):
  try:
    return userPermissionDAO.createUserPermission(db, userPermission.IdUser, userPermission.PermissionList)
  except HTTPException as e: 
    raise e
  
@router.get("/{idUser}/name/{name}", response_model=UserPermissionSchema)
def getUserPermissionByPermissionName(idUser: int, name: str, db: Session = Depends(get_db)):
  try:
    return userPermissionDAO.getUserPermissionByPermissionName(db, idUser, name)
  except HTTPException as e: 
    raise e
  
@router.put("/{idUser}/{idPermission}")
def updateUserPermission(idUser: int, idPermission: int, db: Session = Depends(get_db), user: dict = Depends(authorize(get_db, "PUT: UserPermissions"))):
  try:
    return userPermissionDAO.updateUserPermission(db, idUser, idPermission)
  except HTTPException as e: 
    raise e
  
@router.delete("/{idUser}")
def deleteUserPermission(userPermission: UserPermissionDeleteSchema, db: Session = Depends(get_db), user: dict = Depends(authorize(get_db, "DELETE: UserPermissions"))):
  try:
    return userPermissionDAO.deleteUserPermission(db, userPermission.IdUser, userPermission.PermissionList)
  except HTTPException as e: 
    raise e