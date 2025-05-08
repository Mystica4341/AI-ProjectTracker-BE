from sqlalchemy.orm import Session
from models.permission import Permission
from fastapi import HTTPException

def getPermissionsPagination(db: Session, page: int, pageSize: int, searchTerm: str = None):
    query = db.query(Permission)

    # filter by search term
    if searchTerm:
        query = db.query(Permission).filter(Permission.Name.ilike(f"%{searchTerm}%"))

    # sorting
    query = query.order_by(Permission.IdPermission.asc())

    # pagination
    permissions = query.offset((page - 1) * pageSize).limit(pageSize).all()

    # get total count
    totalCount = db.query(Permission).count()

    # get total pages
    totalPages = (totalCount + pageSize - 1) // pageSize

    return {
        "page": page,
        "pageSize": pageSize,
        "totalCount": totalCount,
        "totalPages": totalPages,
        "data": permissions
    }
    
def getPermissionById(db: Session, id: int):
    permission = db.query(Permission).filter(Permission.IdPermission == id).first()
    if permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    return permission
  
def getPermissionByName(db: Session, name: str):
    permission = db.query(Permission).filter(Permission.Name.ilike(f"%{name}%")).all()
    if permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    return permission
  
def createPermission(db: Session, name: str):
    # check if permission already exists
    existPermission = db.query(Permission).filter(Permission.Name == name).first()
    if existPermission:
        raise HTTPException(status_code=400, detail="Permission already exists")
    
    # create new permission
    permission = Permission(Name=name)
    db.add(permission)
    db.commit()
    db.refresh(permission)
    
    return permission
  
def updatePermission(db: Session, id: int, name: str):
    permission = db.query(Permission).filter(Permission.IdPermission == id).first()
    if permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # check if permission already exists
    existPermission = db.query(Permission).filter(Permission.Name == name).first()
    if existPermission:
        raise HTTPException(status_code=400, detail="Permission already exists")
    
    # update permission
    permission.Name = name
    db.commit()
    db.refresh(permission)
    
    return permission
  
def deletePermission(db: Session, id: int):
    permission = db.query(Permission).filter(Permission.IdPermission == id).first()
    if permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    db.delete(permission)
    db.commit()
    
    return {"detail": "Permission deleted successfully"}

