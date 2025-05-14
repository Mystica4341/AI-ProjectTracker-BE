from sqlalchemy.orm import Session
from models.notification import Notification
from models.user import User
from models.task import Task
from models.todo import Todo
from DAO import userDAO, projectDAO, projectMemberDAO, taskDAO
from fastapi import HTTPException
from datetime import datetime, timedelta, date

def getNotificationsPagination(db: Session, page: int, pageSize: int, searchTerm: str = None):
  query = db.query(Notification).join(User, Notification.IdUser == User.IdUser).add_columns(User.Username)

  # filter by search term
  if searchTerm:
    query = db.query(Notification).filter(Notification.Message.ilike(f"%{searchTerm}%"))

  # sorting
  query = query.order_by(Notification.IdNotification.asc())

  # pagination
  notifications = query.offset((page - 1) * pageSize).limit(pageSize).all()

  # get total count
  totalCount = db.query(Notification).count()

  # get total pages
  totalPages = (totalCount + pageSize - 1) // pageSize

  return {
          "page": page,
          "pageSize": pageSize,
          "totalCount": totalCount,
          "totalPages": totalPages,
          "data": notifications
        }

def createNotification(db: Session, idUser: int, message: str):
  try:
    # check if user exists
    userDAO.getUserById(db, idUser)
  except HTTPException as e:
    raise e

  # create notification
  notification = Notification(IdUser=idUser, Message=message)
  db.add(notification)
  db.commit()
  db.refresh(notification)

  return notification

def getNotificationById(db: Session, id: int):
  notification = db.query(Notification).filter(Notification.IdNotification == id).all()
  if notification is None:
    raise HTTPException(status_code=404, detail="Notification not found")

  for n in notification:
    users = userDAO.getUserById(db, n.IdUser)
    
    n.Username = users.Username

  return notification

def notifyExpiringTasks(db: Session):
    """
    Check for tasks expiring in 1-2 days and create notifications for users.
    """
    try:
        # Get the current date and calculate the range for 1-2 days ahead
        today = datetime.now().date()
        OneDayAhead = today + timedelta(days=1)
        TwoDaysAhead = today + timedelta(days=2)
        
        # Format dates to dd/mm/yyyy for comparison or display
        OneDayAhead_str = OneDayAhead.strftime("%d/%m/%Y")
        TwoDaysAhead_str = TwoDaysAhead.strftime("%d/%m/%Y")

        # Query tasks with due dates within the range
        expiring_todos = db.query(Todo).join(Task, Todo.IdTask == Task.IdTask).filter(
            Task.DueDate.between(OneDayAhead_str, TwoDaysAhead_str)
        ).all()

        for todo in expiring_todos:
            # Get the project member associated with the todo
            project_member = projectMemberDAO.getProjectMemberById(db, todo.IdProjectMember)
            task = taskDAO.getTaskById(db, todo.IdTask)

            # Create a notification for the user
            message = f"Task '{task.Title}' is about to expire on {task.DueDate}. Please take action."
            createNotification(db, project_member.IdUser, message)

        return {"message": f"Notifications created for {len(expiring_todos)} expiring tasks."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error notifying expiring tasks: {str(e)}")
      
def notifyOverdueTasks(db: Session):
    """
    Check for overdue tasks and create notifications for users.
    """
    try:
        # Get the current date
        today = date.today().strftime("%d/%m/%Y")

        # Query tasks with due dates before today
        overdue_todos = db.query(Todo).join(Task, Todo.IdTask == Task.IdTask).filter(
            Task.DueDate < today
        ).all()

        for todo in overdue_todos:
            # Get the project member associated with the todo
            project_member = projectMemberDAO.getProjectMemberById(db, todo.IdProjectMember)
            task = taskDAO.getTaskById(db, todo.IdTask)

            # Create a notification for the user
            message = f"Task '{task.Title}' is overdue. Please take action."
            createNotification(db, project_member.IdUser, message)

        return {"message": f"Notifications created for {len(overdue_todos)} overdue tasks."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error notifying overdue tasks: {str(e)}")
      
def notifyAddedProjectMember(db: Session, idProjectMember: int):
    """
    Notify a user when they are added to a project.
    """
    try:
        # Get the project member details
        member = projectMemberDAO.getProjectMemberById(db, idProjectMember)
        user = userDAO.getUserById(db, member.IdUser)
        project = projectDAO.getProjectById(db, member.IdProject)

        # Create a notification for the user
        message = f"You have been added to project '{project.ProjectName} with role {member.UserRole}'."
        createNotification(db, user.IdUser, message)

        return {"message": f"Notification created for user '{user.Username}'."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error notifying added project member: {str(e)}")
      
def notifyRemovedProjectMember(db: Session, idProjectMember: int):
    """
    Notify a user when they are removed from a project.
    """
    try:
        # Get the project member details
        member = projectMemberDAO.getProjectMemberById(db, idProjectMember)
        user = userDAO.getUserById(db, member.IdUser)
        project = projectDAO.getProjectById(db, member.IdProject)

        # Create a notification for the user
        message = f"You have been removed from project '{project.ProjectName}'."
        createNotification(db, user.IdUser, message)

        return {"message": f"Notification created for user '{user.Username}'."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error notifying removed project member: {str(e)}")
  
def notifyTaskAssigned(db: Session, idTask: int, idUser: int):
    """
    Notify a user when a task is assigned to them.
    """
    try:
        # Get the task details
        task = taskDAO.getTaskById(db, idTask)
        user = userDAO.getUserById(db, idUser)

        # Create a notification for the user
        message = f"You have been assigned to task '{task.Title}'."
        createNotification(db, user.IdUser, message)

        return {"message": f"Notification created for user '{user.Username}'."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error notifying task assignment: {str(e)}")
      
def notifyTaskUpdate(db: Session, idTask: int):
    """
    Notify users when a task is updated.
    """
    try:
        # Get the task details
        task = taskDAO.getTaskById(db, idTask)
        project_members = projectMemberDAO.getProjectMemberByIdProject(db, task.IdProject)

        for member in project_members:
            user = userDAO.getUserById(db, member.IdUser)

            # Create a notification for each user
            message = f"Task '{task.Title}' has been updated to '{task.Status}'."
            createNotification(db, user.IdUser, message)
            
        # Notify the manager of the project
        project = projectDAO.getProjectById(db, task.IdProject)
        manager = userDAO.getUserById(db, project.Manager)

        manager_message = f"Task '{task.Title}' in your project '{project.ProjectName}' has been updated to '{task.Status}'."
        createNotification(db, manager.IdUser, manager_message)
        return {"message": f"Notifications created for {len(project_members)} project members."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error notifying task update: {str(e)}")
      
def notifyManagerAssignedToProject(db: Session, idProject: int):
  """
  Notify a manager when they are assigned to a project by the super admin.
  """
  try:
    # Get the project and manager details
    project = projectDAO.getProjectById(db, idProject)
    manager = userDAO.getUserById(db, project.Manager)
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")

    # Create a notification for the manager
    message = f"You have been assigned as the manager of project '{project.ProjectName}'."
    createNotification(db, manager.IdUser, message)

    return {"message": f"Notification created for manager '{manager.Username}'."}

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error notifying manager assignment: {str(e)}")
      
