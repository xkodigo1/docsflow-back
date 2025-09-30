from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    role: str = Field("operador", pattern="^(admin|operador)$")
    department_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"email": "admin@docsflow.com", "password": "admin123"}
            ]
        }
    }

class UserOut(UserBase):
    id: int
    is_blocked: bool
    failed_attempts: int
    created_at: datetime
    updated_at: datetime
    blocked_at: Optional[datetime] = None
    unblocked_at: Optional[datetime] = None

    class Config:
        orm_mode = True
