from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO.notificationDAO import notifyExpiringTasks, notifyOverdueTasks

app = FastAPI()

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()

# Function to run the notification task
def RunExpiringTasks():
    db: Session = next(get_db())
    notifyExpiringTasks(db)
    
def RunOverdueTasks():
    db: Session = next(get_db())
    notifyOverdueTasks(db)

# Initialize the scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    # Schedule the task to run daily at a specific time (e.g., midnight)
    scheduler.add_job(RunExpiringTasks, "interval", days=1)
    # Schedule the overdue tasks notification to run daily
    scheduler.add_job(RunOverdueTasks, "interval", days=1)
    scheduler.start()