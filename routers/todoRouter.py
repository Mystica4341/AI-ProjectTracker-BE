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

@router.get("/projectMember/{id}", response_model=list[TodoSchema])
def getTodoByIdProjectMember(id: int, db: Session = Depends(get_db)):
  try:
      return todoDAO.getTodoByIdProjectMember(db, id)
  except HTTPException as e:
      raise e

@router.get("/task/{id}", response_model=list[TodoSchema])
def getTodoByIdTask(id: int, db: Session = Depends(get_db)):
  try:
      return todoDAO.getTodoByIdTask(db, id)
  except HTTPException as e:
      raise e

@router.post("/", response_model=TodoSchema, response_model_exclude_none=True)
def createTodo(todo: TodoCreateSchema, db: Session = Depends(get_db)):
  try:
      return todoDAO.createTodo(db, todo.IdProjectMember, todo.IdTask)
  except HTTPException as e:
      raise e

@router.put("/{id}", response_model=TodoSchema, response_model_exclude_none=True)
def updateTodo(id: int, todo: TodoUpdateSchema, db: Session = Depends(get_db)):
  try:
      return todoDAO.updateTodo(db, id, todo.IdProjectMember, todo.IdTask)
  except HTTPException as e:
      raise e

@router.delete("/{id}")
def deleteTodo(id: int, db: Session = Depends(get_db)):
  try:
      return todoDAO.deleteTodo(db, id)
  except HTTPException as e:
      raise e