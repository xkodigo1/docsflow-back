from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    department_id: int
    status: str
    filepath: str

class DocumentCreate(DocumentBase):
    pass

class DocumentOut(DocumentBase):
    id: int
    uploaded_by: int
    uploaded_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        orm_mode = True
