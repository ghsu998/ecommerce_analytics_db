from pydantic import BaseClientCrm
from typing import Optional
from datetime import date

class ClientCrm(BaseClientCrm):
    client_last_contacted: Optional[date]
    client_notes: Optional[str]
    status: str
    client_name: str
    client_company: str
    assigned_to_identity: str
