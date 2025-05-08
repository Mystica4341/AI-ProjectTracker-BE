from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO import permissionDAO, userPermissionDAO
from authentication import authorize
#import Schema
from schemas.userPermissionSchema import UserPermissionSchema, UserPermissionUpdateSchema, UserPermissionCreateSchema, UserPermissionPagination

router = APIRouter()

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()
      
@router.get("/", response_model=UserPermissionPagination)
async def getUserPermissionsPagination(
  db: Session = Depends(get_db), 
  page: int = Query(1, ge=1), 
  pageSize: int = Query(10, ge=1, le=100), 
  searchTerm: str = Query(None), 
  user: dict = Depends(authorize("Admin"))
  ):
  try:
    return userPermissionDAO.getUserPermissionsPagination(db, page, pageSize, searchTerm)
  except HTTPException as e: 
    raise e
  
@router.get("/{idUser}/{idPermission}", response_model=UserPermissionSchema)
async def getUserPermissionById(idUser: int, idPermission: int, db: Session = Depends(get_db)):
  try:
    return userPermissionDAO.getUserPermissionById(db, idUser, idPermission)
  except HTTPException as e: 
    raise e
  
@router.post("/{idUser}/{idPermission}")
async def createUserPermission(idUser: int, idPermission: int, db: Session = Depends(get_db)):
  try:
    return userPermissionDAO.createUserPermission(db, idUser, idPermission)
  except HTTPException as e: 
    raise e
  
@router.get("/{idUser}/name/{name}", response_model=list[UserPermissionSchema])
async def getUserPermissionByName(idUser: int, name: str, db: Session = Depends(get_db)):
  try:
    return userPermissionDAO.getUserPermissionByName(db, idUser, name)
  except HTTPException as e: 
    raise e
  
@router.put("/{idUser}/{idPermission}")
async def updateUserPermission(idUser: int, idPermission: int, db: Session = Depends(get_db)):
  try:
    return userPermissionDAO.updateUserPermission(db, idUser, idPermission)
  except HTTPException as e: 
    raise e
  
@router.delete("/{idUser}/{idPermission}")
async def deleteUserPermission(idUser: int, idPermission: int, db: Session = Depends(get_db)):
  try:
    return userPermissionDAO.deleteUserPermission(db, idUser, idPermission)
  except HTTPException as e: 
    raise e