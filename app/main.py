from fastapi import FastAPI
from app.config import settings

app = FastAPI(title=settings.app_name)

@app.get("/")
async def root():
    return {"message" : "Docsflow Backend"}

@app.get("/ping-config")
def ping_config():
    return {
        "app": settings.app_name
    }

