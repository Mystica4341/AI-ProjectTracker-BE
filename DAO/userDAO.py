from sqlalchemy.orm import Session
from models.user import User
from fastapi import HTTPException
from authentication import hashPassword
from DAO import userPermissionDAO

default_permissions = [
    "GET: Users",
    "POST: Users",
    "PUT: Users",
    "GET: Projects",
    "GET: ProjectMembers",
    "GET: Tasks",
    "PUT: Tasks",
    "GET: Todos",
    "PUT: Todos",
    "GET: ProjectStorage",
    "POST: ProjectStorage",
    "DELETE: ProjectStorage",
    "POST: AI",
    "GET: ChatHistory",
    "POST: ChatHistory",
    "DELETE: ChatHistory"
]

def getUsersPagination(db: Session, page: int, pageSize: int, searchTerm: str = None):
    query =db.query(User)

    # filter by search term
    if searchTerm:
        query = query.filter(User.Username.ilike(f"%{searchTerm}%") | User.Fullname.ilike(f"%{searchTerm}%") | User.Email.ilike(f"%{searchTerm}%") | User.PhoneNumber.ilike(f"%{searchTerm}%"))

    # sorting
    query = query.order_by(User.IdUser.asc())

    # pagination
    users = query.offset((page - 1) * pageSize).limit(pageSize).all()

    # get total count
    totalCount = db.query(User).count()

    # get total pages
    totalPages = (totalCount + pageSize - 1) // pageSize

    return {
            "page": page,
            "pageSize": pageSize,
            "totalCount": totalCount,
            "totalPages": totalPages,
            "data": users
        }

def getUserById(db: Session, id: int):
    user = db.query(User).filter(User.IdUser == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def getUserByEmail(db: Session, email: str):
    user = db.query(User).filter(User.Email == email).first()
    # if user is not None:
    #     raise HTTPException(status_code=400, detail="User's Email already exists")
    if user is None:
        raise HTTPException(status_code=404, detail="User's email not found")
    return user

def getUserByUsername(db: Session, username: str):
    user = db.query(User).filter(User.Username == username).first()
    # if user is not None:
    #     raise HTTPException(status_code=400, detail="User's Username already exists")
    if user is None:
        raise HTTPException(status_code=404, detail="User's username not found")
    return user

def getUserByPhoneNumber(db: Session, phone_number: str):
    user = db.query(User).filter(User.PhoneNumber == phone_number).first()
    # if user is not None:
    #     raise HTTPException(status_code=400, detail="User's Phone Number already exists")
    if user is None:
        raise HTTPException(status_code=404, detail="User's phone number not found")
    return user

def createUser(db: Session, username: str, fullname: str, email: str, password: str, phone_number: str, role: str = None, permission: str = None):
    try:
        # Check if user's email is valid
        existEmail(db, email)
        # Check if user's phone number is valid
        existPhoneNumber(db, phone_number)
        # Check if user's username is valid
        existUsername(db, username)
    except HTTPException as e:
      raise e

    if role == "":
        role = None
    if permission == "":
        permission = None

    user = User(Username=username, Fullname=fullname, Email=email, Password=hashPassword(password), Role=role, Permission=permission, PhoneNumber=phone_number)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    try:
      userPermissionDAO.createUserPermission(db, user.IdUser, default_permissions)
    except HTTPException as e:
      raise e
    
    return user

def updateUser(db: Session, id: int, username: str, fullname: str, email: str, password: str, phone_number: str, role: str = None, permission: str = None):
    try:
      user = getUserById(db, id)
    except HTTPException as e:
      raise e

    try:
        # Check if user's email is valid
        if user.Email != email:
            existEmail(db, email)
        # Check if user's phone number is valid
        if user.PhoneNumber != phone_number:
            existPhoneNumber(db, phone_number)
        # Check if user's username is valid
        if user.Username != username:
            existUsername(db, username)
    except HTTPException as e:
      raise e

    user.Username = username
    user.Fullname = fullname
    user.Email = email
    user.Password = hashPassword(password)
    user.PhoneNumber = phone_number
    user.Role = role
    user.Permission = permission
    db.commit()
    db.refresh(user)
    return user

def updateUserPassword(db: Session, id: int, password: str):
    try:
      user = getUserById(db, id)
    except HTTPException as e:
      raise e

    user.Password = hashPassword(password)
    db.commit()
    db.refresh(user)
    return user

def updateProfileImage(db: Session, id: int, imageURL: str):
    try:
      user = getUserById(db, id)
    except HTTPException as e:
      raise e

    user.ImageUrl = imageURL
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

def existEmail(db: Session, email: str):
  user = db.query(User).filter(User.Email == email).first()
  if user is not None:
        raise HTTPException(status_code=400, detail="User's Email already exists")
  return user

def existPhoneNumber(db: Session, phone_number: str):
  user = db.query(User).filter(User.PhoneNumber == phone_number).first()
  if user is not None:
        raise HTTPException(status_code=400, detail="User's Phone Number already exists")
  return user

def existUsername(db: Session, username: str):
  user = db.query(User).filter(User.Username == username).first()
  if user is not None:
        raise HTTPException(status_code=400, detail="User's Username already exists")
  return user