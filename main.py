from fastapi import FastAPI
import uvicorn
from database import engine, Base
from routers import userRouter, projectRouter

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def root():
  return {"message": "Hello World"}

# Include the user router
app.include_router(userRouter.router, prefix="/users", tags=["users"])

# Include the project router
app.include_router(projectRouter.router, prefix="/projects", tags=["projects"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)