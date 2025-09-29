from fastapi import FastAPI
from config.settings import settings
from utils.db import get_db_connection
from controllers.auth import router as auth_router
from controllers.documents import router as docs_router
from controllers.tables import router as tables_router
from controllers.users import router as users_router

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

application.include_router(auth_router)
application.include_router(docs_router)
application.include_router(tables_router)
application.include_router(users_router)