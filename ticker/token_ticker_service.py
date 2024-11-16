import asyncio
import logging
from typing import List

from login.login_service import LoginService

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)


class TokenTickerService:
    def __init__(self, callback: callable, threaded: bool, login_service: LoginService):
        self.callback = callback
        self.threaded = threaded
        self.kws = login_service.get_kite_websocket()
        self.kws.on_connect = self._on_connect
        self.kws.on_ticks = self._on_ticks
        self.kws.on_close = self._on_close

        # Note: In-memory model instead of redis
        self.tokens = set()

    def add_tokens(self, tokens: List[int]):
        if self.kws.is_connected():
            self.kws.close()
        self.tokens.add(tokens)
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
        lst_tokens = list(self.tokens)
        ws.subscribe(lst_tokens)
        ws.set_mode(ws.MODE_FULL, lst_tokens)
        logger.debug(f"Subscribed to {len(self.tokens)} tokens")

    def _on_ticks(self, ws, ticks):
        logger.debug(f'Received ticks {ticks}')
        if self.threaded:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.callback(ticks))
        else:
            self.callback(ticks)
        logger.debug("Executed callback")

    def _on_close(self, ws, code, response):
        logger.error(f'Stopping ticker due to code {code}, response: {response}')
        if self.threaded:
            asyncio.get_event_loop().close()
        if ws.is_connected():
            ws.stop()
            logger.debug('Websocket stopped')
        else:
            logger.error('Websocket kite is already closed!!')
