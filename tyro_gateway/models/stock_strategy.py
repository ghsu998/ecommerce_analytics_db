# models/stock_strategy.py

from pydantic import BaseModel, Field, model_validator
from datetime import date

class StockStrategy(BaseModel):
    title: str = Field(..., description="Notion 主索引欄位，建議用 ticker + trade_action")
    strategy_date: date = Field(..., description="操作日期")
    trade_action: str = Field(..., description="操作方向，如 Buy / Sell / Hold")
    ticker: str = Field(..., description="股票代碼，如 AAPL")
    position_size: float = Field(..., description="持倉數量 / 比例")
    strike_price: float = Field(..., description="目標價格或建倉價格")
    strategy_note: str = Field(default="", description="策略說明或備註")
    unique_key: str = Field(..., description="唯一識別碼，建議用 ticker + trade_action + strategy_date")

    @model_validator(mode="before")
    @classmethod
    def auto_title(cls, values):
        if not values.get("title"):
            ticker = values.get("ticker", "")
            action = values.get("trade_action", "")
            values["title"] = f"{ticker} {action}".strip()
        return values


