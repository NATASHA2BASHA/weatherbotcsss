from fastapi import FastAPI
from app.database.models import Base, engine
from app.api.routes import router as api_router
from app.api.admin import router as admin_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Weather bot is running"}

app.include_router(api_router, prefix="/api")
app.include_router(admin_router)
