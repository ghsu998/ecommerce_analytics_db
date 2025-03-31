from pydantic import BaseModel
from typing import Optional

class EmailIdentity(BaseModel):
    language: str
    used_for: str
    tone_style: str
    identity_name: str
    example_phrase: Optional[str] = ""
