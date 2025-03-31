from pydantic import BaseModel

class Strategy(BaseModel):
    notes: str
    category: str
    objective: str
    module_or_project: str
    phase: str
    strategy_name: str
