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
        self.ws = None
        self.kws.on_connect = self._on_connect
        self.kws.on_ticks = self._on_ticks
        self.kws.on_close = self._on_close

        # Note: In-memory model instead of redis
        self.tokens = set()

    def add_tokens(self, tokens: List[int]):
        if not tokens:
            return
        if self.kws.is_connected():
            self.kws.close()
        self.tokens.update(tokens)
        self.kws.connect(threaded=self.threaded)

    def delete_tokens(self, tokens: List[int]):
        if not tokens:
            return
        if self.ws.is_connected():
            self.ws.stop()
            logger.info('Websocket closed successfully!')
        else:
            logger.info('Websocket kite already closed! Please ignore.')
        if self.kws.is_connected():
            self.kws.close()
        self.tokens.difference_update(tokens)
        if len(self.tokens) > 0:
            self.kws.connect(threaded=self.threaded)

    def delete_all_tokens(self):
        self.tokens = set()
        if self.ws.is_connected():
            self.ws.stop()
            logger.info('Websocket closed successfully!')
        else:
            logger.info('Websocket kite already closed! Please ignore.')
        if self.kws.is_connected():
            self.kws.close()

    def _on_connect(self, ws, response):
        if self.threaded:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.info(f"Started event loop")
        lst_tokens = list(self.tokens)
        self.ws = ws
        ws.subscribe(lst_tokens)
        ws.set_mode(ws.MODE_FULL, lst_tokens)
        logger.info(f"Subscribed to {len(self.tokens)} tokens")

    def _on_ticks(self, ws, ticks):
        logger.debug(f'Received ticks {ticks}')
        try:
            if self.threaded:
                loop = asyncio.get_event_loop()
                task = loop.create_task(self.callback(ticks))
                loop.run_until_complete(task)
            else:
                self.callback(ticks)
            logger.debug("Executed callback")
        except Exception as e:
            logger.error(f'Error in callback: {e}')
            self.kws.close()

    def _on_close(self, ws, code, response):
        logger.error(f'Stopping ticker due to code {code}, response: {response}')
        if ws.is_connected():
            ws.stop()
            logger.info('Websocket closed successfully!')
        else:
            logger.info('Websocket kite already closed! Please ignore.')
        if self.threaded:
            if not asyncio.get_event_loop().is_closed():
                asyncio.get_event_loop().close()
                logger.debug("Closed event loop")
