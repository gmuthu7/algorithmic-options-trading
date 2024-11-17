from datetime import date, datetime
from typing import Dict

from pydantic import field_serializer
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
    ce: Dict[int, TickModel]  # strike: TickModel
    pe: Dict[int, TickModel]  # strike: TickModel
    timestamp: datetime


class StockQuoteModel(JsonModel):
    # pk = stock
    stock: str
    timestamp: datetime

    # @field_serializer('timestamp')
    # def serialize_dt(self, timestamp: datetime, _info):
    #     return timestamp.timestamp()

    tick: TickModel
