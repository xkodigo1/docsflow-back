from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    role: str = Field(..., pattern="^(admin|operador)$")
    department_id: Optional[int] = None
    is_blocked: bool = False
    failed_attempts: int = 0

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    blocked_at: Optional[datetime] = None
    unblocked_at: Optional[datetime] = None

    class Config:
        orm_mode = True
