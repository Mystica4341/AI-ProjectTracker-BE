from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "Users"

    IdUser = Column(Integer, primary_key=True, index=True)
    Email = Column(String, unique=True, index=True)
    Fullname = Column(String)
    Username = Column(String, unique=True, index=True)
    Password = Column(String)
    Role = Column(Enum("Super Admin", "Admin", "User"), default="User")
    Permission = Column(String, default="none")
    PhoneNumber = Column(String)
    ImageUrl = Column(String)