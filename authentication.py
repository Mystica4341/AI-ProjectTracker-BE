from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import secrets
from pydantic import BaseModel
from DAO import userDAO
from fastapi.security import OAuth2PasswordBearer

# Secret key for JWT
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256" 
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashPassword(password):
    haseshedPassword = pwd_context.hash(password)
    print(haseshedPassword)
    return haseshedPassword

def verifyPassword(password, hashedPassword):
    return pwd_context.verify(password, hashedPassword)

def getHashedPassword(password):
    return pwd_context.hash(password)

def createAccessToken(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticateUser(db: Session, username: str, password: str):
    user = userDAO.getUserByUsername(db, username)
    if not user:
        return False
    if not verifyPassword(password, user.Password):
        return False
    return user

def getCurrentUser(token: str = Depends(oauth2_scheme)):
  try:
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      Username: str = payload.get("sub")
      if Username is None:
          raise HTTPException(status_code=401, detail="Invalid token")
      return {"Username": Username, "Role": payload.get("Role"), "IdUser": payload.get("IdUser")}
  except JWTError:
      raise HTTPException(status_code=401, detail="Invalid token")

def authorize(role: str):
  def _authorize(user: dict = Depends(getCurrentUser)):
    if user["Role"] == "Super Admin":
        return user
    if user is None or user["Role"] != role:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user
  return _authorize