from sqlalchemy.orm import Session
from models.todo import Todo
from models.user import User
from fastapi import HTTPException
from DAO import taskDAO, projectMemberDAO

def getTodoById(db: Session, id: int):
  todo = db.query(Todo).filter(Todo.IdTodo == id).first()
  if todo is None:
    raise HTTPException(status_code=404, detail="Todo not found")
  
  try:
    task = taskDAO.getTaskById(db, todo.IdTask)
    projectMember = projectMemberDAO.getProjectMemberById(db, todo.IdProjectMember)
  except HTTPException as e:
    raise e

  # Attach additional fields to the ORM object (if needed)
  todo.ProjectName = projectMember.ProjectName
  todo.Fullname = projectMember.Fullname
  todo.Email = projectMember.Email
  todo.Title = task.Title
  todo.Status = task.Status
  todo.DueDate = task.DueDate
  todo.Priority = task.Priority

  return todo

  # return {
  #   "IdTodo": dbTodo.IdTodo,
  #   "IdProjectMember": dbTodo.IdProjectMember,
  #   "Fullname": "hi",
  #   "IdTask": dbTodo.IdTask,
  #   # "Title": task.Title,
  #   # "Status": task.Status,
  #   # "DueDate": task.DueDate,
  #   # "Priority": task.Priority,
  # }

def getTodoByIdUser(db: Session, idUser: int, idTask: int):
  try:
    todo = db.query(Todo).filter(Todo.IdUser == idUser).all()
    user = userDAO.getUserById(db, idUser)
    task = taskDAO.getTaskById(db, idTask)
    return {
      "IdTodo": todo.IdTodo,
      "IdUser": todo.IdUser,
      "IdTask": todo.IdTask,
      "Title": task.Title,
      "Status": task.Status,
      "DueDate": task.DueDate,
      "Priority": task.Priority,
    }
  except HTTPException as e:
    raise e