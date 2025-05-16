from fastapi import APIRouter, Depends, HTTPException, Query 
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO import notificationDAO

router = APIRouter()

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()
      
@router.get("/")
def getNotificationsPagination(
  db: Session = Depends(get_db),
  page: int = Query(1, ge=1), # page number, default is 1 and must be greater than 1
  pageSize: int = Query(10, ge=1, le=100), # limit of items per page, default is 10 and must be between 1 and 100
  searchTerm: str = Query(None), # search query, default is None
):
  try:
    return notificationDAO.getNotificationsPagination(db, page, pageSize, searchTerm)
  except HTTPException as e:
    raise e
  
@router.get("/{id}")
def getNotificationByIdUser(id: int, db: Session = Depends(get_db)):
  try:
    return notificationDAO.getNotificationByIdUser(db, id)
  except HTTPException as e:
    raise e
  
@router.post("/")
def createNotification(idUser: int, message: str, db: Session = Depends(get_db)):
  try:
    return notificationDAO.createNotification(db, idUser, message)
  except HTTPException as e:
    raise e
  
@router.delete("/{id}")
def deleteNotification(id: int, db: Session = Depends(get_db)):
  try:
    return notificationDAO.deleteNotification(db, id)
  except HTTPException as e:
    raise e
  
@router.delete("/user/{id}")
def deleteNotificationByIdUser(id: int, db: Session = Depends(get_db)):
  try:
    return notificationDAO.deleteAllNotificationsByIdUser(db, id)
  except HTTPException as e:
    raise e


