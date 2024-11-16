import asyncio
import logging
from collections import defaultdict
from datetime import datetime, date
from typing import Dict, List, Callable

from redis_om import NotFoundError

from info.info_model import StockInfoModel, OptionInfoModel
from info.info_service import InfoService
from login.login_service import LoginService
from setting import TICKER_THREADED
from ticker.ticker_model import StockQuoteModel, OptionQuoteModel, TickModel
from ticker.token_ticker_service import TokenTickerService

logger = logging.getLogger(__name__)


class TickerService:

    def __init__(self, info_service: InfoService, login_Service: LoginService):
        self._info_service = info_service
        self._ticker_service = TokenTickerService(self.callback, TICKER_THREADED, login_Service)
        self._stock_observers = defaultdict(list)
        self._option_observers = defaultdict(list)

    def add_stock(self, stock: str):
        if self._check_if_stock_exists(stock):
            return
        stock_info = self._info_service.get_stock_info(stock)
        self._ticker_service.add_tokens([stock_info.instrument_token])
        stock = StockQuoteModel(pk=stock, stock=stock)
        stock.save()

    def add_option(self, stock: str, expiry: datetime):
        if self._check_if_stock_exists(stock):
            return
        option_info = self._info_service.get_option_info(stock, expiry)
        self._ticker_service.add_tokens(list(option_info.instruments.keys()))
        option = OptionQuoteModel(pk=self._get_primary_key(stock, expiry), stock=stock, expiry=expiry)
        option.save()

    def delete_stock(self, stock: str):
        if not self._check_if_stock_exists(stock):
            return
        stock_info = self._info_service.get_stock_info(stock)
        self._ticker_service.delete_tokens([stock_info.instrument_token])

    def delete_option(self, stock: str, expiry: datetime):
        if not self._check_if_option_exists(stock, expiry):
            return
        option_info = self._info_service.get_option_info(stock, expiry)
        self._ticker_service.delete_tokens(list(option_info.instruments.keys()))

    def callback(self, ticks: List[Dict]):
        for pk in StockQuoteModel.all_pks():
            quote = StockQuoteModel.get(pk)
            info = StockInfoModel.get(quote.stock)
            for tick in ticks:
                if info.instrument_token == tick["instrument_token"]:
                    quote.tick = TickModel(open=tick["ohlc"]["open"], high=tick["ohlc"]["high"],
                                           low=tick["ohlc"]["low"], close=tick["ohlc"]["close"], ltp=tick["last_price"])
                    quote.timestamp = datetime.now()
                    quote.save()
                    break
        for pk in OptionQuoteModel.all_pks():
            quote = OptionQuoteModel.get(pk)
            info = OptionInfoModel.get(self._get_primary_key(quote.stock, quote.expiry))
            for tick in ticks:
                for instrument in info.instruments:
                    if instrument == tick["instrument_token"]:
                        strike = instrument
                        quote.tick = TickModel(open=tick["ohlc"]["open"], high=tick["ohlc"]["high"],
                                               low=tick["ohlc"]["low"], close=tick["ohlc"]["close"],
                                               ltp=tick["last_price"])
                        quote.timestamp = datetime.now()
                        quote.save()
                        break

    def _publish_stock(self, stock: str, quote: StockQuoteModel):
        for observer in self._stock_observers[stock]:
            observer(quote)

    def _publish_option(self, stock: str, expiry: datetime, quote: OptionQuoteModel):
        for observer in self._option_observers[self._get_primary_key(stock, expiry)]:
            observer(quote)

    def subscribe_stock(self, stock: str, callable: Callable):
        self._stock_observers[stock].append(callable)

    def subscribe_option(self, stock: str, expiry: datetime, callable: Callable):
        self._option_observers[self._get_primary_key(stock, expiry)].append(callable)

    def _check_if_stock_exists(self, stock: str):
        try:
            StockQuoteModel.get(stock)
        except NotFoundError:
            return False
        return True

    def _check_if_option_exists(self, stock: str, expiry: datetime):
        try:
            OptionQuoteModel.get(self._get_primary_key(stock, expiry))
        except NotFoundError:
            return False

    def _get_primary_key(self, stock: str, expiry: date):
        return f"{stock}_{expiry}"
