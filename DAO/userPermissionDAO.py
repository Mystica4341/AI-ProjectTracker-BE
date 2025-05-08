from sqlalchemy.orm import Session
from models.userPermission import UserPermission
from models.permission import Permission
from models.user import User
from fastapi import HTTPException

from DAO import userDAO, permissionDAO

def getUserPermissionsPagination(db: Session, page: int, pageSize: int, searchTerm: str = None):
    query = db.query(UserPermission).join(Permission, UserPermission.IdPermission == Permission.IdPermission).join(User, UserPermission.IdUser == User.IdUser)
    
    # filter by search term
    if searchTerm:
        query = query.filter(User.Username.ilike(f"%{searchTerm}%") | User.Email.ilike(f"%{searchTerm}%") | Permission.Name.ilike(f"%{searchTerm}%"))
        
    # sorting
    query = query.order_by(UserPermission.IdUser.asc())
    
    # pagination
    userPermissions = query.offset((page - 1) * pageSize).limit(pageSize).all()

    # get total count
    totalCount = db.query(UserPermission).count()

    # get total pages
    totalPages = (totalCount + pageSize - 1) // pageSize
    
    # append and format data
    for up in userPermissions:
        permission = permissionDAO.getPermissionById(db, up.IdPermission)
        user = userDAO.getUserById(db, up.IdUser)
        
        up.PermissionName = permission.Name
        up.Username = user.Username
        up.Email = user.Email
        
    return {
        "page": page,
        "pageSize": pageSize,
        "totalCount": totalCount,
        "totalPages": totalPages,
        "data": userPermissions
    }
    
def getUserPermissionById(db: Session, idUser: int, idPermission: int):
    userPermission = db.query(UserPermission).filter(UserPermission.IdUser == idUser | UserPermission.IdPermission == idPermission).all()
    if userPermission is None:
        raise HTTPException(status_code=404, detail="User permission not found")
      
    for up in userPermission:
        permission = permissionDAO.getPermissionById(db, up.IdPermission)
        user = userDAO.getUserById(db, up.IdUser)
        
        up.PermissionName = permission.Name
        up.Username = user.Username
        up.Email = user.Email
    
    return userPermission
  
def getUserPermissionByName(db: Session, idUser: int, name: str):
    userPermission = db.query(UserPermission).join(Permission, UserPermission.IdPermission == Permission.IdPermission)
    
    userPermission = userPermission.filter(UserPermission.IdUser.ilike(f"%{idUser}%") & Permission.Name.ilike(f"%{name}%")).all()
    
    if not userPermission:
        raise HTTPException(status_code=404, detail="User permission not found")
    
    # Append additional data for each user permission
    for up in userPermission:
        permission = permissionDAO.getPermissionById(db, up.IdPermission)
        user = userDAO.getUserById(db, up.IdUser)
        
        up.PermissionName = permission.Name
        up.Username = user.Username
        up.Email = user.Email
    
    return userPermission
  
def createUserPermission(db: Session, idUser: int, idPermission: int):
    # check if user exists
    try:
        userDAO.existUser(db, idUser)
    except HTTPException as e:
        raise e
    
    # check if permission exists
    try:
        permissionDAO.existPermission(db, idPermission)
    except HTTPException as e:
        raise e
    
    # check if user permission already exists
    existUserPermission = db.query(UserPermission).filter(UserPermission.IdUser == idUser & UserPermission.IdPermission == idPermission).first()
    if existUserPermission:
        raise HTTPException(status_code=400, detail="User permission already exists")
    
    # create new user permission
    userPermission = UserPermission(IdUser=idUser, IdPermission=idPermission)
    db.add(userPermission)
    db.commit()
    db.refresh(userPermission)
    
    return userPermission
  
def updateUserPermission(db: Session, idUser: int, idPermission: int):
    # check if user exists
    try:
        userDAO.existUser(db, idUser)
    except HTTPException as e:
        raise e
    
    # check if permission exists
    try:
        permissionDAO.existPermission(db, idPermission)
    except HTTPException as e:
        raise e
    
    # check if user permission exists
    userPermission = db.query(UserPermission).filter(UserPermission.IdUser == idUser & UserPermission.IdPermission == idPermission).first()
    if userPermission is None:
        raise HTTPException(status_code=404, detail="User permission not found")
    
    # update user permission
    userPermission.IdUser = idUser
    userPermission.IdPermission = idPermission
    db.commit()
    db.refresh(userPermission)
    
    return userPermission
  
def deleteUserPermission(db: Session, idUser: int, idPermission: int):
    # check if user exists
    try:
        userDAO.existUser(db, idUser)
    except HTTPException as e:
        raise e
    
    # check if permission exists
    try:
        permissionDAO.existPermission(db, idPermission)
    except HTTPException as e:
        raise e
    
    # check if user permission exists
    userPermission = db.query(UserPermission).filter(UserPermission.IdUser == idUser & UserPermission.IdPermission == idPermission).first()
    if userPermission is None:
        raise HTTPException(status_code=404, detail="User permission not found")
    
    # delete user permission
    db.delete(userPermission)
    db.commit()
    
    return {"detail": "User permission disabled successfully"}