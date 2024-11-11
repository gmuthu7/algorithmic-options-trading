from datetime import date, datetime
from typing import Dict, List

from redis_om import JsonModel, EmbeddedJsonModel


# Info Models
class InstrumentModel(EmbeddedJsonModel):
    strike: int
    trading_symbol: str
    instrument_type: str


class OptionInfoModel(JsonModel):
    # pk = f"{stock}_{expiry}"
    stock: str
    expiry: date
    instruments: Dict[int, InstrumentModel]  # instrument_token: KiteInstrumentModel
    timestamp: datetime


class StockInfoModel(JsonModel):
    # pk = stock
    stock: str
    instrument_token: int
    expiries: List[date]
    timestamp: datetime
    lot_size: int
