from datetime import date, datetime
from datetime import date, datetime
from typing import Dict

from redis_om import JsonModel, EmbeddedJsonModel


# Quote Models
class KiteTickModel(EmbeddedJsonModel):
    ltp: float
    trading_symbol: str
    open: float
    high: float
    low: float
    close: float

 
class KiteOptionQuoteModel(JsonModel):
    # pk = f"{stock}_{expiry}"
    stock: str
    expiry: date
    ce: Dict[int, KiteTickModel]  # strike: TickModel
    pe: Dict[int, KiteTickModel]  # strike: TickModel
    timestamp: datetime


class KiteStockQuoteModel(JsonModel):
    # pk = stock
    stock: str
    timestamp: datetime
    tick: KiteTickModel
