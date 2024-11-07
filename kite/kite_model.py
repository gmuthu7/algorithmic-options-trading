import os
from datetime import date, datetime
from typing import Optional, Dict, List

from redis_om import JsonModel, EmbeddedJsonModel, HashModel, Field

from setting import KITE_CREDENTIALS_KEY


# Info Models
class KiteInstrumentModel(EmbeddedJsonModel):
    strike: int
    trading_symbol: str
    instrument_type: str


class KiteOptionInfoModel(JsonModel):
    # pk = f"{stock}_{expiry}"
    stock: str
    expiry: date
    instruments: Dict[int, KiteInstrumentModel]  # instrument_token: KiteInstrumentModel
    timestamp: datetime


class KiteStockInfoModel(JsonModel):
    # pk = stock
    stock: str
    instrument_token: int
    expiries: List[date]
    timestamp: datetime
    lot_size: int


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


# Credentials Model
class KiteCredentialsModel(HashModel):
    primary_key: str = Field(default=KITE_CREDENTIALS_KEY, primary_key=True)
    api_key: str = Field(default=os.getenv("KITE_API_KEY"))
    api_secret: str = Field(default=os.getenv("KITE_API_SECRET"))
    access_token: Optional[str] = None
