from pydantic import BaseEmailIdentity
from typing import Optional
from datetime import date

class EmailIdentity(BaseEmailIdentity):
    language: str
    used_for: str
    tone_style: str
    identity_name: str
    example_phrase: Optional[str]
