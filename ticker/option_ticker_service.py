import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Callable

from redis_om import NotFoundError

import helper
from info.info_model import OptionInfoModel
from info.info_service import InfoService
from login.login_service import LoginService
from setting import TICKER_THREADED
from ticker.ticker_model import OptionQuoteModel, TickModel
from ticker.token_ticker_service import TokenTickerService

logger = logging.getLogger(__name__)


class OptionTickerService:

    def __init__(self, info_service: InfoService, login_service: LoginService):
        self._info_service = info_service
        self._login_service = login_service
        self._option_observers = defaultdict(list)
        self._ticker_service = TokenTickerService(self.callback, TICKER_THREADED, login_service)
        self._login_service.register_observer(self.login_callback)

    def login_callback(self, status):
        if status == "CONNECTED":
            self._ticker_service.delete_all_tokens()
            tokens = []
            for pk in OptionQuoteModel.all_pks():
                option = OptionQuoteModel.get(pk)
                option_info = self._info_service.get_option_info(option.stock, option.expiry)
                tokens.extend([option_info.ce[strike].instrument_token for strike in option_info.ce])
                tokens.extend([option_info.pe[strike].instrument_token for strike in option_info.pe])
                self._ticker_service.add_tokens(tokens)
        else:
            pass

    def callback(self, ticks: List[Dict]):
        for pk in OptionQuoteModel.all_pks():
            quote = OptionQuoteModel.get(pk)
            quote.timestamp = datetime.now()
            info = OptionInfoModel.get(helper.get_primary_key(quote.stock, quote.expiry))
            for tick in ticks:
                self._populate_ticks(quote.ce, info.ce, tick)
                self._populate_ticks(quote.pe, info.pe, tick)
            quote.save()
            self._publish_option(quote)

    def add_option(self, stock: str, expiry: datetime):
        if self._check_if_option_exists(stock, expiry):
            return
        tokens = []
        option_info = self._info_service.get_option_info(stock, expiry)
        tokens.extend([option_info.ce[strike].instrument_token for strike in option_info.ce])
        tokens.extend([option_info.pe[strike].instrument_token for strike in option_info.pe])
        self._ticker_service.add_tokens(tokens)
        option = OptionQuoteModel(pk=helper.get_primary_key(stock, expiry), stock=stock, expiry=expiry)
        option.save()

    def delete_option(self, stock: str, expiry: datetime):
        if not self._check_if_option_exists(stock, expiry):
            return
        option_info = self._info_service.get_option_info(stock, expiry)
        self._ticker_service.delete_tokens(list(option_info.instruments.keys()))

    def subscribe_option(self, stock: str, expiry: datetime, callable: Callable):
        self._option_observers[helper.get_primary_key(stock, expiry)].append(callable)

    def _populate_ticks(self, strike_tick_mapping, strike_info_mapping, tick):
        for strike, instrument in strike_info_mapping.items():
            instrument_token = instrument.instrument_token
            if instrument_token == tick["instrument_token"]:
                strike_tick_mapping[strike] = TickModel(open=tick["ohlc"]["open"], high=tick["ohlc"]["high"],
                                                        low=tick["ohlc"]["low"], close=tick["ohlc"]["close"],
                                                        ltp=tick["last_price"])
                break

    def _publish_option(self, quote: OptionQuoteModel):
        for observer in self._option_observers[helper.get_primary_key(quote.stock, quote.expiry)]:
            observer(quote)

    def _check_if_option_exists(self, stock: str, expiry: datetime):
        try:
            OptionQuoteModel.get(helper.get_primary_key(stock, expiry))
        except NotFoundError:
            return False
