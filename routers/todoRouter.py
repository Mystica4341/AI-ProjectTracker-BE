from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO import todoDAO
#import Schema
from schemas.todoSchema import TodoSchema, TodoCreateSchema, TodoUpdateSchema, TodoPaginationSchema
from authentication import authorize

router = APIRouter()

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()

@router.get("/", response_model=TodoPaginationSchema)
def getTodoPagination(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1), # page number, default is 1 and must be greater than 1
    pageSize: int = Query(10, ge=1, le= 100), # limit of items per page, default is 10 and must be between 1 and 100
    searchTerm: str = Query(None), # search query, default is None
    user: dict = Depends(authorize(get_db, "GET: Todos")),
    ):
    try:
        return todoDAO.getTodosPagination(db, page, pageSize, searchTerm)
    except HTTPException as e:
        raise e

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

@router.get("/task/{title}", response_model=list[TodoSchema])
def getTodoByTaskTitle(title: str, db: Session = Depends(get_db)):
  try:
      return todoDAO.getTodoByTaskTitle(db, title)
  except HTTPException as e:
      raise e

@router.post("/", response_model=TodoSchema, response_model_exclude_none=True)
def createTodo(todo: TodoCreateSchema, db: Session = Depends(get_db), user: dict = Depends(authorize(get_db, "POST: Todos"))):
  try:
      return todoDAO.createTodo(db, todo.IdProjectMember, todo.IdTask)
  except HTTPException as e:
      raise e

@router.put("/{id}", response_model=TodoSchema, response_model_exclude_none=True)
def updateTodo(id: int, todo: TodoUpdateSchema, db: Session = Depends(get_db), user: dict = Depends(authorize(get_db, "PUT: Todos"))):
  try:
      return todoDAO.updateTodo(db, id, todo.IdProjectMember, todo.IdTask)
  except HTTPException as e:
      raise e

@router.delete("/{id}")
def deleteTodo(id: int, db: Session = Depends(get_db), user: dict = Depends(authorize(get_db, "DELETE: Todos"))):
  try:
      return todoDAO.deleteTodo(db, id)
  except HTTPException as e:
      raise e