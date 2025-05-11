from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm
from authentication import createAccessToken, SECRET_KEY, ALGORITHM, authenticateUser, getCurrentUser
from DAO import userDAO, userPermissionDAO

router = APIRouter()

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

@router.post("/token")
async def login(formData: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
  user = authenticateUser(db, formData.username, formData.password)
  
  permissions = userPermissionDAO.getUserPermissionByIdUser(db, user.IdUser)
  permistionsList = []
  for permission in permissions:
      permistionsList.append(permission.PermissionName)

  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Incorrect username or password",
      headers={"WWW-Authenticate": "Bearer"},
    )
  Token = createAccessToken(data={"sub": user.Username, "Role": user.Role, "IdUser": user.IdUser, "permissions": permistionsList})
  return {"access_token": Token, "token_type": "bearer"}

@router.get("/protected-route")
def protected_route(current_user: dict = Depends(getCurrentUser)):
    return {"Username": current_user["Username"], "Role": current_user["Role"], "IdUser": current_user["IdUser"], "permissions": current_user["permissions"]}

@router.get("/current-user-permissions")
def getCurrentUserPermissions(db: Session = Depends(get_db), user: dict = Depends(getCurrentUser)):
    permissions = userPermissionDAO.getUserPermissionByIdUser(db, user["IdUser"])
    permistionsList = []
    for permission in permissions:
        permistionsList.append(permission.PermissionName)
    return permistionsList