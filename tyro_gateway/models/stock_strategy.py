# models/stock_strategy.py

from pydantic import BaseModel, Field
from datetime import date

class StockStrategy(BaseModel):
    title: str = Field(..., description="Notion 主索引欄位，建議用 ticker + action")
    strategy_date: date = Field(..., description="操作日期")
    action: str = Field(..., description="操作方向，如 Buy / Sell / Hold")
    ticker: str = Field(..., description="股票代碼，如 AAPL")
    position_size: float = Field(..., description="持倉張數 / 比例")
    strike_price: float = Field(..., description="目標價格或建倉價格")
    strategy_note: str = Field(default="", description="策略說明或備註")
