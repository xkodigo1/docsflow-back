from pydantic import BaseModel
from datetime import datetime

class PasswordResetTokenBase(BaseModel):
    user_id: int
    token: str
    expires_at: datetime
    used: bool = False

class PasswordResetTokenCreate(PasswordResetTokenBase):
    pass

class PasswordResetTokenOut(PasswordResetTokenBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
