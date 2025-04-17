from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO import todoDAO
#import Schema
from schemas.todoSchema import TodoSchema, TodoCreateSchema, TodoUpdateSchema

router = APIRouter()

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()

@router.get("/{id}", response_model=TodoSchema)
def getTodoById(id: int, db: Session = Depends(get_db)):
  try:
      return todoDAO.getTodoById(db, id)
  except HTTPException as e:
      raise e


