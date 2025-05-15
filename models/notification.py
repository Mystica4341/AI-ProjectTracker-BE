from sqlalchemy import Column, Integer, String, Date, Enum
from database import Base
from datetime import datetime

class Notification(Base):
  __tablename__ = "Notifications"

  IdNotification = Column(Integer, primary_key=True, index=True)
  IdUser = Column(Integer)
  Message = Column(String)
  DateCreate = Column(String, default=lambda: datetime.now().strftime("%d/%m/%Y %H:%M"))