from sqlalchemy import Column, Integer, String, Enum
from database import Base

class UserPermission(Base):
    __tablename__ = "UserPermissions"

    IdPermission = Column(Integer, primary_key=True)
    IdUser = Column(Integer, primary_key=True)