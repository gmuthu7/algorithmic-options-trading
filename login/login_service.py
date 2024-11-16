import logging
from datetime import datetime
from typing import Callable

from kiteconnect import KiteConnect, KiteTicker
from redis_om import NotFoundError

import helper
import singleton
from login.login_model import CredentialsModel
from setting import KITE_LOGIN_URL, KITE_CREDENTIALS_KEY

logger = logging.getLogger(__name__)


class LoginService:

    def __init__(self):
        cred = self._get_credentials_from_redis()
        self._kite_connect = KiteConnect(cred.api_key, cred.access_token)
        self._kws = KiteTicker(cred.api_key, cred.access_token)
        self._observers = []  # pub-sub
        # cred: KiteCredentialsModel in redis

    def set_request_token(self, request_token: str):
        cred = self._get_credentials_from_redis()
        data = KiteConnect(cred.api_key, cred.access_token).generate_session(request_token, api_secret=cred.api_secret)
        cred.access_token = data["access_token"]
        cred.timestamp = datetime.now()
        cred.save()
        helper.set_expiry_of_model_to_daily(cred)  # TODO: Use kite's session_expiry_hook instead
        self._update_instances()

    def get_login_uri(self):
        cred = self._get_credentials_from_redis()
        return KITE_LOGIN_URL % cred.api_key

    def is_logged_in(self):
        try:
            cred = CredentialsModel.get(KITE_CREDENTIALS_KEY)
            if not cred or not cred.access_token:
                return False
            return True
        except NotFoundError:
            logger.info("Kite Credentials not found, need to relogin")
            return False

    def get_kite_connect(self):
        return self._kite_connect

    def get_kite_websocket(self):
        return self._kws

    def register_observer(self, callback: Callable):
        self._observers.append(callback)
        if self.is_logged_in():
            callback("CONNECTED")
        else:
            callback("DISCONNECTED")

    def delete_observer(self, callback: Callable):
        self._observers.remove(callback)

    def _notify_observers(self, state: str):
        for callback in self._observers:
            callback(state)

    def _get_credentials_from_redis(self):
        try:
            return CredentialsModel.get(KITE_CREDENTIALS_KEY)
        except NotFoundError:
            logger.info("Saving kite credentials in Redis")
            return CredentialsModel().save()

    def _update_instances(self):
        cred = CredentialsModel.get(KITE_CREDENTIALS_KEY)
        self._kite_connect = KiteConnect(cred.api_key, cred.access_token)
        self._kws = KiteTicker(cred.api_key, cred.access_token)
        self._notify_observers("CONNECTED")
        logger.info("Kite is connected!")
