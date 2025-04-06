# models/options_strategy.py

from pydantic import BaseModel, Field
from datetime import date

class OptionsStrategy(BaseModel):
    title: str = Field(..., description="Notion 主索引欄位，可等同 option_strategy 或 ticker")
    created_date: date = Field(..., description="建立日期")
    action: str = Field(..., description="操作類型，例如 Buy / Sell")
    option_strategy: str = Field(..., description="選擇權策略名稱，例如 Covered Call")
    ticker: str = Field(..., description="標的代碼，如 AAPL")
    delta: float = Field(..., description="Greeks 中的 Delta 值")
    expiration: date = Field(..., description="選擇權到期日")
    entry_option_price: float = Field(..., description="進場選擇權價格")
    contract_size: int = Field(..., description="合約單位（通常為 100）")
    strategy_note: str = Field(default="", description="額外說明")
