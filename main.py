from fastapi import FastAPI, Depends
import uvicorn
from typing import Annotated
from database import engine, Base
from routers import userRouter, projectRouter, taskRouter, projectMemberRouter, todoRouter, authRouter, projectStorageRouter
from AI import aiRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to match the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}

# Include the authentication router
app.include_router(authRouter.router, prefix="/api", tags=["auth"])

# Include the user router
app.include_router(userRouter.router, prefix="/api/users", tags=["users"])

# Include the project router
app.include_router(projectRouter.router, prefix="/api/projects", tags=["projects"])

# Include the project storage router
app.include_router(projectStorageRouter.router, prefix="/api/storages", tags=["storages"])

# Include the task router
app.include_router(taskRouter.router, prefix="/api/tasks", tags=["tasks"])

# Include the project member router
app.include_router(projectMemberRouter.router, prefix="/api/members", tags=["members"])

# Include the todo router
app.include_router(todoRouter.router, prefix="/api/todos", tags=["todos"])

# Include the AI router
app.include_router(aiRouter.router, prefix="/api/ai", tags=["AI"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)