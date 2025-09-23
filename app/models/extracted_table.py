from pydantic import BaseModel
from typing import Any
from datetime import datetime

class ExtractedTableBase(BaseModel):
    document_id: int
    table_index: int
    content: Any  # Puede ser dict o list, depende del procesamiento

class ExtractedTableCreate(ExtractedTableBase):
    pass

class ExtractedTableOut(ExtractedTableBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
