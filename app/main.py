from fastapi import FastAPI
from config.settings import settings
from utils.db import get_db_connection
from controllers.auth import router as auth_router
from controllers.documents import router as documents_router
from controllers.tables import router as tables_router
from controllers.users import router as users_router
from fastapi.middleware.cors import CORSMiddleware

application = FastAPI()

# CORS
application.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
application.include_router(tables_router)
application.include_router(users_router)
application.include_router(documents_router)