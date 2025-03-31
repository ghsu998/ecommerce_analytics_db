from pydantic import BaseModel
from typing import Optional
from datetime import date

class ClientCRM(BaseModel):
    client_name: str
    client_company: str
    status: str
    assigned_to_identity: str
    client_notes: Optional[str] = ""
    client_last_contacted: Optional[date] = None
