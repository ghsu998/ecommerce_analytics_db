# models/strategy.py

from pydantic import BaseModel, Field, model_validator

class Strategy(BaseModel):
    title: str = Field(..., description="Notion 主索引欄位，建議等同 strategy_name")
    strategy_name: str = Field(..., description="策略名稱，例如 GreeneWrap PPC Phase 1")
    module_project: str = Field(..., description="所屬模組或專案名稱")
    category: str = Field(..., description="分類標籤，例如 Amazon PPC、SEO、BD")
    phase: str = Field(..., description="策略所處階段")
    objective: str = Field(..., description="本策略目的或目標")
    notes: str = Field(default="", description="Markdown 說明、備註、執行細節")
    unique_key: str = Field(..., description="唯一識別碼，建議用 strategy_name + module_project + category")

    @model_validator(mode="before")
    @classmethod
    def auto_title(cls, values):
        if not values.get("title"):
            values["title"] = values.get("strategy_name", "")
        return values

