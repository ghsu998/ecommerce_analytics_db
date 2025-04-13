# models/email_identity.py

from pydantic import BaseModel, Field

class EmailIdentity(BaseModel):
    title: str = Field(..., description="Notion 主索引欄位，建議等同 identity_name")
    identity_name: str = Field(..., description="Email 身分標籤，例如 'Gary | Personal'")
    language: str = Field(..., description="使用語言（例如 English）")
    tone_style: str = Field(..., description="語氣風格，例如 Professional, Friendly")
    used_for: str = Field(..., description="主要用途，例如 Brand Communication")
    example_phrase: str = Field(default="", description="常用語句範本")
    notes: str = Field(default="", description="其他備註，例如角色背景、特殊需求")
    unique_key: str = Field(..., description="唯一識別碼，建議使用 email_identity 的 identity_name")
