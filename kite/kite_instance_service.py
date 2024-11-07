import logging
import time
import webbrowser
from threading import Thread
from typing import Optional

from kiteconnect import KiteConnect, KiteTicker
from redis_om import NotFoundError

from kite.kite_model import KiteCredentialsModel
from setting import KITE_LOGIN_URL, KITE_CREDENTIALS_KEY, KITE_ACCESS_TOKEN_TTL

logger = logging.getLogger(__name__)


class KiteInstanceService:
    # This call is thread safe since its used only by the spawned thread and not the main thread
    def __init__(self):
        self._default_login_uri = KITE_LOGIN_URL
        self._kite_connect: Optional[KiteConnect] = None
        self._kws: Optional[KiteTicker] = None
        if self._is_access_token_invalid():
            KiteCredentialsModel().save()
            Thread(target=self._kite_login).start()
        cred = KiteCredentialsModel.get(KITE_CREDENTIALS_KEY)
        self._update_instances(cred)

    def set_request_token(self, request_token: str):
        cred = KiteCredentialsModel()
        data = KiteConnect(cred.api_key, cred.access_token).generate_session(request_token, api_secret=cred.api_secret)
        cred.access_token = data["access_token"]
        cred.save()
        cred.expire(KITE_ACCESS_TOKEN_TTL)
        self._update_instances(cred)

    def get_kite_connect(self):
        if self._is_access_token_invalid():
            self._kite_login()
        return self._kite_connect

    def get_kite_websocket(self):
        if self._is_access_token_invalid():
            self._kite_login()
        return self._kws

    def _update_instances(self, cred: KiteCredentialsModel):
        self._kite_connect = KiteConnect(cred.api_key, cred.access_token)
        self._kws = KiteTicker(cred.api_key, cred.access_token)

    def _kite_login(self):
        logger.info("Sleeping for 3 seconds before opening browser for login")
        time.sleep(3)
        dummy_model = KiteCredentialsModel()
        login_url = self._default_login_uri % dummy_model.api_key
        webbrowser.open(login_url)

    def _is_access_token_invalid(self):
        try:
            cred = KiteCredentialsModel.get(KITE_CREDENTIALS_KEY)
            if not cred.access_token:
                return True
            return False
        except NotFoundError:
            logger.info("Kite Credentials not found")
            return True
