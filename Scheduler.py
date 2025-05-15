from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from database import SessionLocal
from DAO.notificationDAO import notifyExpiringTasks, notifyOverdueTasks

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()

# Function to run the notification task
def RunExpiringTasks():
    print("Running Expiring Tasks...")
    db: Session = next(get_db())
    notifyExpiringTasks(db)
    
def RunOverdueTasks():
    print("Running Overdue Tasks...")
    db: Session = next(get_db())
    notifyOverdueTasks(db)

# Initialize the scheduler
def start_scheduler():
    """
    For testing purposes, change the time to run the tasks immediately.
    """
    scheduler = BackgroundScheduler()
    # Schedule to run at 2:30 AM daily
    scheduler.add_job(RunExpiringTasks, 'cron', hour=10, minute=48)
    # Schedule to run at 6:00 PM daily
    scheduler.add_job(RunOverdueTasks, 'cron', hour=18, minute=0)
    
    # print("Running tasks immediately for testing...")
    # RunExpiringTasks()
    # RunOverdueTasks()
        
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")