from pydantic import BaseApiTrigger
from typing import Optional
from datetime import date

class ApiTrigger(BaseApiTrigger):
    timestamp: date
    trigger_source: str
    status: str
    data_summary: str
    endpoint: str
    action_name: str
