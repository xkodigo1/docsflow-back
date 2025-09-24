from fastapi import APIRouter
from services.auth_service import login_user

router = APIRouter()

@router.post("/login")
def login(username: str, password: str):
    return login_user(username, password)
