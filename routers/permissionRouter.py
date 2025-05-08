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
async def getPermissionsPagination(
  db: Session = Depends(get_db), 
  page: int = Query(1, ge=1), 
  pageSize: int = Query(10, ge=1, le=100), 
  searchTerm: str = Query(None), 
  user: dict = Depends(authorize("Admin"))
  ):
  try:
    return permissionDAO.getPermissionsPagination(db, page, pageSize, searchTerm)
  except HTTPException as e: 
    raise e
  
@router.get("/{id}")
async def getPermissionById(id: int, db: Session = Depends(get_db)):
  try:
    return permissionDAO.getPermissionById(db, id)
  except HTTPException as e: 
    raise e
  
@router.get("/name/{name}")
async def getPermissionByName(name: str, db: Session = Depends(get_db)):
  try:
    return permissionDAO.getPermissionByName(db, name)
  except HTTPException as e: 
    raise e
  
@router.post("/")
async def createPermission(permission: str, db: Session = Depends(get_db)):
  try:
    return permissionDAO.createPermission(db, permission)
  except HTTPException as e: 
    raise e
  
@router.put("/{id}")
async def updatePermission(id: int, permission: str, db: Session = Depends(get_db)):
  try:
    return permissionDAO.updatePermission(db, id, permission)
  except HTTPException as e: 
    raise e
  
@router.delete("/{id}")
async def deletePermission(id: int, db: Session = Depends(get_db)):
  try:
    return permissionDAO.deletePermission(db, id)
  except HTTPException as e: 
    raise e
  
