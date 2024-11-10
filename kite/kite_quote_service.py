import asyncio
import logging
from datetime import datetime
from typing import Dict, List

from redis_om import NotFoundError

from kite.kite_info_service import KiteInfoService
from kite.kite_login_service import KiteInstanceService
from kite.kite_model import KiteStockQuoteModel, KiteOptionQuoteModel
from setting import KITE_TICKER_THREADED

logger = logging.getLogger(__name__)


class KiteQuoteService:

    def __init__(self, kite_info_service: KiteInfoService, kite_instance_service: KiteInstanceService):
        self.kite_info_service = kite_info_service
        self.kite_ticker_service = KiteTickerService(self.callback, KITE_TICKER_THREADED, kite_instance_service)

    def add_stock(self, stock: str):
        if self._check_if_stock_exists(stock):
            return
        stock_info = self.kite_info_service.get_stock_info(stock)
        self.kite_ticker_service.add_tokens([stock_info.instrument_token])

    def add_option(self, stock: str, expiry: datetime):
        if self._check_if_stock_exists(stock):
            return
        option_info = self.kite_info_service.get_option_info(stock, expiry)
        self.kite_ticker_service.add_tokens(list(option_info.instruments.keys()))

    def delete_stock(self, stock: str):
        if not self._check_if_stock_exists(stock):
            return
        stock_info = self.kite_info_service.get_stock_info(stock)
        self.kite_ticker_service.delete_tokens([stock_info.instrument_token])

    def delete_option(self, stock: str, expiry: datetime):
        if not self._check_if_option_exists(stock, expiry):
            return
        option_info = self.kite_info_service.get_option_info(stock, expiry)
        self.kite_ticker_service.delete_tokens(list(option_info.instruments.keys()))

    def callback(self, ticks: List[Dict]):
        pass

    def _check_if_stock_exists(self, stock: str):
        try:
            KiteStockQuoteModel.get(stock)
        except NotFoundError:
            return False
        return True

    def _check_if_option_exists(self, stock: str, expiry: datetime):
        try:
            KiteOptionQuoteModel.get(self._get_primary_key(stock, expiry))
        except NotFoundError:
            return False

    def _get_primary_key(self, stock: str, expiry: datetime):
        return f"{stock}_{expiry}"


class KiteTickerService:
    def __init__(self, callback: callable, threaded: bool, kite_instance_service: KiteInstanceService):
        self.callback = callback
        self.threaded = threaded
        self.kws = kite_instance_service.get_kite_websocket()
        self.kws.on_connect = self._on_connect
        self.kws.on_ticks = self._on_ticks
        self.kws.on_close = self._on_close

        # Note: In-memory model instead of redis
        self.tokens = []

    def add_tokens(self, tokens: List[int]):
        if self.kws.is_connected():
            self.kws.close()
        self.tokens.extend(tokens)
        self.kws.connect(threaded=self.threaded)

    def delete_tokens(self, tokens: List[int]):
        if self.kws.is_connected():
            self.kws.close()
        for token in tokens:
            self.tokens.remove(token)
        self.kws.connect(threaded=self.threaded)

    def _on_connect(self, ws, response):
        if self.threaded:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.debug(f"Started event loop")
        ws.subscribe(self.tokens)
        ws.set_mode(ws.MODE_FULL, self.tokens)
        logger.debug(f"Subscribed to {len(self.tokens)} tokens")

    def _on_ticks(self, ws, ticks):
        logger.debug(f'Received ticks {ticks}')
        if self.threaded:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.callback(ticks))
            logger.debug("Executed callback")
        else:
            self.callback(ticks)

    def _on_close(self, ws, code, response):
        logger.error(f'Stopping ticker due to code {code}, response: {response}')
        if self.threaded:
            asyncio.get_event_loop().close()
        if ws.is_connected():
            ws.stop()
            logger.debug('Websocket stopped')
        else:
            logger.error('Websocket kite is already closed!!')
