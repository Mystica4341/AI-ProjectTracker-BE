from sqlalchemy import Column, Integer, String, Enum
from database import Base

class Permission(Base):
    __tablename__ = "Permissions"

    IdPermission = Column(Integer, primary_key=True, index=True)
    Name = Column(String)