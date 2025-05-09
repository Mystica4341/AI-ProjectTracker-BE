from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO import permissionDAO
from authentication import authorize
#import Schema

router = APIRouter()

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()

@router.get("/")
def getPermissionsPagination(
  db: Session = Depends(get_db), 
  page: int = Query(1, ge=1), 
  pageSize: int = Query(10, ge=1, le=100), 
  searchTerm: str = Query(None), 
  user: dict = Depends(authorize(get_db, "GET: Permissions")),
  ):
  try:
    return permissionDAO.getPermissionsPagination(db, page, pageSize, searchTerm)
  except HTTPException as e: 
    raise e
  
@router.get("/{id}")
def getPermissionById(id: int, db: Session = Depends(get_db), user: dict = Depends(authorize(get_db, "GET: Permissions"))):
  try:
    return permissionDAO.getPermissionById(db, id)
  except HTTPException as e: 
    raise e
  
@router.get("/name/{name}")
def getPermissionByName(name: str, db: Session = Depends(get_db), user: dict = Depends(authorize(get_db, "GET: Permissions"))):
  try:
    return permissionDAO.getPermissionByName(db, name)
  except HTTPException as e: 
    raise e
  
@router.post("/")
def createPermission(permission: str, db: Session = Depends(get_db), user: dict = Depends(authorize(get_db, "POST: Permissions"))):
  try:
    return permissionDAO.createPermission(db, permission)
  except HTTPException as e: 
    raise e
  
@router.put("/{id}")
def updatePermission(id: int, permission: str, db: Session = Depends(get_db), user: dict = Depends(authorize(get_db, "PUT: Permissions"))):
  try:
    return permissionDAO.updatePermission(db, id, permission)
  except HTTPException as e: 
    raise e
  
@router.delete("/{id}")
def deletePermission(id: int, db: Session = Depends(get_db), user: dict = Depends(authorize(get_db, "DELETE: Permissions"))):
  try:
    return permissionDAO.deletePermission(db, id)
  except HTTPException as e: 
    raise e
  
