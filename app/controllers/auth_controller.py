from fastapi import APIRouter
from services.auth_service import login_user
from schemas.user import UserLogin

router = APIRouter()

@router.post("/login")
def login(credentials: UserLogin):
    return login_user(credentials.email, credentials.password)