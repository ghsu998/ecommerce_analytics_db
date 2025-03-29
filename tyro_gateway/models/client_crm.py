#models/client_crm.py

from pydantic import BaseModel
from datetime import date
from typing import Optional

class ClientCRMInput(BaseModel):
    client_name: str
    client_company: str
    status: str
    assigned_to_identity: str
    client_notes: Optional[str] = ""
    client_last_contacted: Optional[date] = None
