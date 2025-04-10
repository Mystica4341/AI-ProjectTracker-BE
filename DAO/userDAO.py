from sqlalchemy.orm import Session
from models.user import User
from fastapi import HTTPException

def getAllUsers(db: Session):
    return db.query(User).all()

def getUserById(db: Session, id: int):
    user = db.query(User).filter(User.IdUser == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def getUserByEmail(db: Session, email: str):
    user = db.query(User).filter(User.Email == email).first()
    # if user is None:
    #     raise HTTPException(status_code=404, detail="User's email not found")
    if user is not None:
        raise HTTPException(status_code=400, detail="User's Email already exists")
    return user

def getUserByUsername(db: Session, username: str):
    user = db.query(User).filter(User.Username == username).first()
    # if user is None:
    #     raise HTTPException(status_code=404, detail="User's username not found")
    if user is not None:
        raise HTTPException(status_code=400, detail="User's Username already exists")
    return user

def getUserByPhoneNumber(db: Session, phone_number: str):
    user = db.query(User).filter(User.PhoneNumber == phone_number).first()
    # if user is None:
    #     raise HTTPException(status_code=404, detail="User's phone number not found")
    if user is not None:
        raise HTTPException(status_code=400, detail="User's Phone Number already exists")
    return user

def createUser(db: Session, username: str, fullname: str, email: str, password: str, phone_number: str):
    try:
        # Check if user's email is valid
        getUserByEmail(db, email)
        # Check if user's phone number is valid
        getUserByPhoneNumber(db, phone_number)
        # Check if user's username is valid
        getUserByUsername(db, username)
    except HTTPException as e:
      raise e

    user = User(Username=username, Fullname=fullname, Email=email, Password=password, PhoneNumber=phone_number)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def updateUser(db: Session, id: int, username: str, fullname: str, email: str, password: str, phone_number: str, role: str, permission: str):
    try:
        # Check if user's email is valid
        getUserByEmail(db, email)
        # Check if user's phone number is valid
        getUserByPhoneNumber(db, phone_number)
        # Check if user's username is valid
        getUserByUsername(db, username)
    except HTTPException as e:
      raise e
      
    try:
      user = getUserById(db, id)
    except HTTPException as e:
      raise e
    user.Username = username
    user.Fullname = fullname
    user.Email = email
    user.Password = password
    user.PhoneNumber = phone_number
    user.Role = role
    user.Permission = permission
    db.commit()
    db.refresh(user)
    return user

def deleteUser(db: Session, id: int):
    try:
      user = getUserById(db, id)
    except HTTPException as e:
      raise e
    db.delete(user)
    db.commit()
    return {"details": "User deleted successfully"}