# models/personal_tax.py

from pydantic import BaseModel, Field, model_validator
from datetime import date

class PersonalTax(BaseModel):
    title: str = Field(..., description="Notion 主索引欄位，建議對應 tax_platform + year")
    filing_date: date = Field(..., description="報稅日期")
    tax_platform: str = Field(..., description="報稅平台名稱，例如 TurboTax、FreeTaxUSA")
    year: int = Field(..., description="申報稅的年度")
    agi: float = Field(..., description="Adjusted Gross Income（調整後總所得）")
    total_tax: float = Field(..., description="應繳稅額總計")
    withholding_paid: float = Field(..., description="已預扣的稅金")
    refund_due: float = Field(..., description="應退稅額")
    notes: str = Field(default="", description="備註內容")
    unique_key: str = Field(..., description="唯一識別碼，建議使用 tax_platform + year")

    @model_validator(mode="before")
    @classmethod
    def auto_title(cls, values):
        if not values.get("title"):
            platform = values.get("tax_platform", "")
            year = values.get("year", "")
            values["title"] = f"{platform} {year}".strip()
        return values



