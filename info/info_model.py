from datetime import date, datetime
from typing import Dict, List

from redis_om import JsonModel, EmbeddedJsonModel


# Info Models
class InstrumentModel(EmbeddedJsonModel):
    trading_symbol: str
    instrument_token: int


class OptionInfoModel(JsonModel):
    # pk = f"{stock}_{expiry}"
    stock: str
    expiry: date
    ce: Dict[int, InstrumentModel]  # strike: InstrumentModel
    pe: Dict[int, InstrumentModel]  # strike: InstrumentModel
    timestamp: datetime


class StockInfoModel(JsonModel):
    # pk = stock
    stock: str
    instrument_token: int
    expiries: List[date]
    timestamp: datetime
    lot_size: int
