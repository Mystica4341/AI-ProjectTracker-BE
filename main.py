from fastapi import FastAPI
import uvicorn
from database import engine, Base
from routers import userRouter, projectRouter, taskRouter, projectMemberRouter, todoRouter
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

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

# Include the user router
app.include_router(userRouter.router, prefix="/api/users", tags=["users"])

# Include the project router
app.include_router(projectRouter.router, prefix="/api/projects", tags=["projects"])

# Include the task router
app.include_router(taskRouter.router, prefix="/api/tasks", tags=["tasks"])

# Include the project member router
app.include_router(projectMemberRouter.router, prefix="/api/members", tags=["members"])

# Include the todo router
app.include_router(todoRouter.router, prefix="/api/todos", tags=["todos"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)