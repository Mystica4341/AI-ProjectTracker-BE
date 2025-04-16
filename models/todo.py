from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "Todos"

    IdTodo = Column(Integer, primary_key=True, index=True)
    IdProjectMember = Column(Integer)
    IdTask = Column(Integer)