# models/strategy.py

from pydantic import BaseModel, Field

class Strategy(BaseModel):
    title: str = Field(..., description="Notion 主索引欄位，建議等同 strategy_name")
    strategy_name: str = Field(..., description="策略名稱，例如 GreeneWrap PPC Phase 1")
    module_or_project: str = Field(..., description="所屬模組或專案名稱")
    category: str = Field(..., description="分類標籤，例如 Amazon PPC、SEO、BD")
    phase: str = Field(..., description="策略所處階段")
    objective: str = Field(..., description="本策略目的或目標")
    notes: str = Field(default="", description="Markdown 說明、備註、執行細節")
