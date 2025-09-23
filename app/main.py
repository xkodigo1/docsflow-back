from fastapi import FastAPI
from config import settings
from utils.db import get_db_connection

application = FastAPI()

@application.on_event("startup")
def startup_event():
    connection = get_db_connection()
    if connection:
        application.state.db_connection = connection
    else:
        application.state.db_connection = None

@application.on_event("shutdown")
def shutdown_event():
    connection = getattr(application.state, "db_connection", None)
    if connection:
        connection.close()

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
    conn = getattr(application.state, "db_connection", None)
    if conn and conn.is_connected():
        return {"db_status": "Conexión exitosa"}
    else:
        return {"db_status": "Error de conexión"}