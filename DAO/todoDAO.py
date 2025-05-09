from sqlalchemy.orm import Session
from models.todo import Todo
from models.projectMember import ProjectMember
from models.task import Task
from fastapi import HTTPException
from DAO import taskDAO, projectMemberDAO

def getTodosPagination(db: Session, page: int, pageSize: int, searchTerm: str = None):
  query = db.query(Todo).join(ProjectMember, Todo.IdProjectMember == ProjectMember.IdProjectMember).join(Task, Todo.IdTask == Task.IdTask)

  # filter by search term
  if searchTerm:
    query = query.filter(Task.Title.ilike(f"%{searchTerm}%") | Task.Status.ilike(f"%{searchTerm}%") | Task.Priority.ilike(f"%{searchTerm}%"))

  # sorting
  query = query.order_by(Todo.IdTodo.asc())

  # pagination
  todos = query.offset((page - 1) * pageSize).limit(pageSize).all()

  # get total count
  totalCount = db.query(Todo).count()

  # get total pages
  totalPages = (totalCount + pageSize - 1) // pageSize

  # append and format data
  for t in todos:
    projectMember = getProjectMemberDetail(db, t.IdProjectMember)
    task = getTaskDetail(db, t.IdTask)
    
    t.ProjectName = projectMember.ProjectName
    t.Fullname = projectMember.Fullname
    t.Email = projectMember.Email
    t.Title = task.Title
    t.Status = task.Status
    t.DueDate = task.DueDate
    t.Priority = task.Priority

  return {
          "page": page,
          "pageSize": pageSize,
          "totalCount": totalCount,
          "totalPages": totalPages,
          "data": todos
        }

def getTodoById(db: Session, id: int):
  todo = db.query(Todo).filter(Todo.IdTodo == id).first()
  if todo is None:
    raise HTTPException(status_code=404, detail="Todo not found")
  
  # Get additional information from other tables
  projectMember = getProjectMemberDetail(db, todo.IdProjectMember)
  task = getTaskDetail(db, todo.IdTask)

  # append data
  todo.ProjectName = projectMember.ProjectName
  todo.Fullname = projectMember.Fullname
  todo.Email = projectMember.Email
  todo.Title = task.Title
  todo.Status = task.Status
  todo.DueDate = task.DueDate
  todo.Priority = task.Priority

  return todo

def getTodoByIdProjectMember(db: Session, idProjectMember: int):
  todo = db.query(Todo).filter(Todo.IdProjectMember == idProjectMember).all()
  if todo is None:
    raise HTTPException(status_code=404, detail="Todo not found")
  
  # append data
  for t in todo:
    projectMember = getProjectMemberDetail(db, t.IdProjectMember)
    task = getTaskDetail(db, t.IdTask)
    
    t.ProjectName = projectMember.ProjectName
    t.Fullname = projectMember.Fullname
    t.Email = projectMember.Email
    t.Title = task.Title
    t.Status = task.Status
    t.DueDate = task.DueDate
    t.Priority = task.Priority

  return todo

def getTodoByTaskTitle(db: Session, title: int):
  todo = db.query(Todo).join(Task, Todo.IdTask == Task.IdTask).filter(Task.Title.ilike(f"%{title}%")).order_by(Task.Title.asc()).all()
  if todo is None:
    raise HTTPException(status_code=404, detail="Todo not found")
  
  # append data
  for t in todo:
    projectMember = getProjectMemberDetail(db, t.IdProjectMember)
    task = getTaskDetail(db, t.IdTask)
    
    t.ProjectName = projectMember.ProjectName
    t.Fullname = projectMember.Fullname
    t.Email = projectMember.Email
    t.Title = task.Title
    t.Status = task.Status
    t.DueDate = task.DueDate
    t.Priority = task.Priority

  return todo

def createTodo(db: Session, IdProjectMember: int, IdTask: int):
  try:
    existTodo(db, IdProjectMember, IdTask)
  except HTTPException as e:
    raise e
  todo = Todo(IdProjectMember=IdProjectMember, IdTask=IdTask)
  db.add(todo)
  db.commit()
  db.refresh(todo)
  return todo

def updateTodo(db: Session, id: int, IdProjectMember: int, IdTask: int):
  try:
    existTodo(db, IdProjectMember, IdTask)
    todo = getTodoById(db, id)
  except HTTPException as e:
    raise e
  todo.IdProjectMember = IdProjectMember
  todo.IdTask = IdTask
  db.commit()
  db.refresh(todo)
  return todo

def deleteTodo(db: Session, id: int):
  todo = getTodoById(db, id)
  db.delete(todo)
  db.commit()
  return {"detail": "Todo deleted successfully"}

def getProjectMemberDetail(db: Session, idProjectMember: int):
  try:
    projectMember = projectMemberDAO.getProjectMemberById(db, idProjectMember)
    return projectMember
  except HTTPException as e:
    raise e

def getTaskDetail(db: Session, idTask: int):
  try:
    task = taskDAO.getTaskById(db, idTask)
    return task
  except HTTPException as e:
    raise e

def existTodo(db: Session, IdProjectMember: int, IdTask: int):
  try:
    projectMemberDAO.getProjectMemberById(db, IdProjectMember)
  except:
    raise HTTPException(status_code=404, detail="There is no project member with id: " + str(IdProjectMember))

  try:
    taskDAO.getTaskById(db, IdTask)
  except:
    raise HTTPException(status_code=404, detail="There is no task with id: " + str(id))