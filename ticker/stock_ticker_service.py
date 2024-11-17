import logging
from datetime import datetime
from typing import Dict, List

from redis.asyncio import Redis

from info.info_model import StockInfoModel
from info.info_service import InfoService
from login.login_service import LoginService
from setting import TICKER_THREADED, STOCK_STREAM_KEY
from ticker.ticker_model import StockQuoteModel, TickModel
from ticker.token_ticker_service import TokenTickerService

logger = logging.getLogger(__name__)


class StockTickerService:

    def __init__(self, info_service: InfoService, login_service: LoginService, r: Redis):
        self._info_service = info_service
        self._ticker_service = TokenTickerService(self.callback, TICKER_THREADED, login_service)
        self._r = r
        self.stocks = []

    async def callback(self, ticks: List[Dict]):
        for stock in self.stocks:
            info = StockInfoModel.get(stock)
            for tick in ticks:
                if info.instrument_token == tick["instrument_token"]:
                    tick = TickModel(open=tick["ohlc"]["open"], high=tick["ohlc"]["high"],
                                     low=tick["ohlc"]["low"], close=tick["ohlc"]["close"], ltp=tick["last_price"])
                    quote = StockQuoteModel(pk=stock, stock=stock, timestamp=datetime.now(), tick=tick)
                    quote.save()
                    await self.publish_stock(quote)
                    break

    def add_stock(self, stock: str):
        stock_info = self._info_service.get_stock_info(stock)
        self._ticker_service.add_tokens([stock_info.instrument_token])
        self.stocks.append(stock)

    def delete_stock(self, stock: str):
        stock_info = self._info_service.get_stock_info(stock)
        self._ticker_service.delete_tokens([stock_info.instrument_token])
        self.stocks.remove(stock)

    def add_all_stocks(self, stocks: List[str]):
        if not stocks:
            return
        tokens = []
        for stock in stocks:
            stock_info = self._info_service.get_stock_info(stock)
            tokens.append(stock_info.instrument_token)
        self._ticker_service.add_tokens(tokens)
        self.stocks = stocks

    def delete_all_stocks(self):
        tokens = []
        for stock in self.stocks:
            stock_info = self._info_service.get_stock_info(stock)
            tokens.append(stock_info.instrument_token)
        self._ticker_service.delete_tokens(tokens)
        self.stocks = []

    async def publish_stock(self, quote: StockQuoteModel):
        json = quote.model_dump_json()
        await self._r.xadd(f"{STOCK_STREAM_KEY}:{quote.stock}", {"data": json})
