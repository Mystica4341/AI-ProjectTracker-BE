from sqlalchemy.orm import Session
from models.notification import Notification
from models.user import User
from models.task import Task
from models.todo import Todo
from models.projectMember import ProjectMember
from DAO import userDAO, projectDAO, projectMemberDAO, taskDAO
from fastapi import HTTPException
from datetime import datetime, timedelta, date

def getNotificationsPagination(db: Session, page: int, pageSize: int, searchTerm: str = None):
  query = db.query(Notification).join(User, Notification.IdUser == User.IdUser)

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
  
  for n in notifications:
    users = userDAO.getUserById(db, n.IdUser)
    
    n.Username = users.Username

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

def getNotificationByIdUser(db: Session, idUser: int):
  notification = db.query(Notification).filter(Notification.IdUser == idUser).all()
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
        
        print(expiring_todos)

        for todo in expiring_todos:
            # Get the project member associated with the todo
            project_member = projectMemberDAO.getProjectMemberById(db, todo.IdProjectMember)
            task = taskDAO.getTaskById(db, todo.IdTask)
            
            if Task.Status != "Completed":

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
            
            # Check if the task is not completed
            if Task.Status != "Completed":

              # Create a notification for the user
              message = f"Task '{task.Title}' is overdue. Please take action."
              createNotification(db, project_member.IdUser, message)

        return {"message": f"Notifications created for {len(overdue_todos)} overdue tasks."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error notifying overdue tasks: {str(e)}")
      
def notifyAddedProjectMember(db: Session, idProject: int, idUser: int, userRole: str):
    """
    Notify a user when they are added to a project.
    """
    try:
        # Get the project member details
        # member = projectMemberDAO.getProjectMemberById(db, idProjectMember)
        try:
          user = userDAO.getUserById(db, idUser)
          project = projectDAO.getProjectById(db, idProject)
        except HTTPException as e:
          raise e

        # Create a notification for the user
        message = f"You have been added to project '{project.ProjectName}' with role '{userRole}'."
        createNotification(db, idUser, message)

        return {"message": f"Notification created for user '{user.Username}'."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error notifying added project member: {str(e)}")
      
def notifyRemovedProjectMember(db: Session, idProject: int, idUser: int):
    """
    Notify a user when they are removed from a project.
    """
    try:
        # Get the project member details
        try:
          user = userDAO.getUserById(db, idUser)
          project = projectDAO.getProjectById(db, idProject)
        except HTTPException as e:
          raise e

        # Create a notification for the user
        message = f"You have been removed from project '{project.ProjectName}'."
        createNotification(db, idUser, message)

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
        todo = db.query(Todo).filter(Todo.IdTask == idTask).all()
        for t in todo:
            member = db.query(ProjectMember).filter(ProjectMember.IdProjectMember == t.IdProjectMember).all()
            for m in member:
                # Get the project member details
                try:
                    user = userDAO.getUserById(db, m.IdUser)
                    project = projectDAO.getProjectById(db, task.IdProject)
                except HTTPException as e:
                    raise e

                # Create a notification for the user
                message = f"Task '{task.Title}' in project '{project.ProjectName}' which your role is '{m.UserRole}' has been updated to '{task.Status}'."
                createNotification(db, user.IdUser, message)
            
        # Notify the manager of the project
        try:
          manager = userDAO.getUserById(db, project.Manager)
        except HTTPException as e:
          raise HTTPException(status_code=404, detail="Manager in Project not found")

        manager_message = f"Task '{task.Title}' in your project '{project.ProjectName}' has been updated to '{task.Status}'."
        createNotification(db, manager.IdUser, manager_message)
        return {"message": f"Notifications created for {len(user.Username)} project members."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error notifying task update: {str(e)}")
      
def notifyManagerAssignedToProject(db: Session, idProject: int, idManager: int):
  """
  Notify a manager when they are assigned to a project by the super admin.
  """
  try:
    # Get the project and manager details
    project = projectDAO.getProjectById(db, idProject)
    manager = userDAO.getUserById(db, idManager)
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")

    # Create a notification for the manager
    message = f"You have been assigned as the manager of project '{project.ProjectName}'."
    createNotification(db, manager.IdUser, message)

    return {"message": f"Notification created for manager '{manager.Username}'."}

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error notifying manager assignment: {str(e)}")
      
