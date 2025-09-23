from fastapi import FastAPI
from config import settings
from utils.db import get_db_connection

application = FastAPI()

@application.get("/")
async def root():
    return {"message" : "Docsflow Backend"}

@application.get("/ping-db")
def ping_db():
    return {"db_user": settings.db_user, 
            "db_host": settings.db_host,
            "db_name": settings.db_name}

@application.get("/db-status")
def db_status():
    conn = get_db_connection()
    if conn:
        conn.close()
        return {"db_status": "Conexión exitosa"}
    else:
        return {"db_status": "Error de conexión"}