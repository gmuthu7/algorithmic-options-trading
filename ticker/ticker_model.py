from datetime import date, datetime
from typing import Dict

from redis_om import JsonModel, EmbeddedJsonModel, Field


# Quote Models
class TickModel(EmbeddedJsonModel):
    ltp: float
    open: float
    high: float
    low: float
    close: float


class OptionQuoteModel(JsonModel):
    # pk = f"{stock}_{expiry}"
    stock: str
    expiry: date
    ce: Dict[int, TickModel] = Field(default={})  # strike: TickModel
    pe: Dict[int, TickModel] = Field(default={})  # strike: TickModel
    timestamp: datetime = Field(default=None)


class StockQuoteModel(JsonModel):
    # pk = stock
    stock: str
    timestamp: datetime = Field(default=None)
    tick: TickModel = Field(default=None)
