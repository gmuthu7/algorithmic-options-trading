import logging
from datetime import datetime, timedelta
from typing import Optional

from kiteconnect import KiteConnect, KiteTicker
from redis_om import NotFoundError

from kite.kite_model import KiteCredentialsModel
from setting import KITE_LOGIN_URL, KITE_CREDENTIALS_KEY, KITE_CREDENTIALS_TTL

logger = logging.getLogger(__name__)


class KiteLoginService:
    def __init__(self):
        self._kite_connect: Optional[KiteConnect] = None
        self._kws: Optional[KiteTicker] = None
        # cred: KiteCredentialsModel in redis
        if self.is_logged_in():
            self._update_instances()

    def set_request_token(self, request_token: str):
        cred = self._get_credentials_from_redis()
        data = KiteConnect(cred.api_key, cred.access_token).generate_session(request_token, api_secret=cred.api_secret)
        cred.access_token = data["access_token"]
        cred.save()
        self._set_key_with_daily_expiry(cred)
        self._update_instances()

    def _set_key_with_daily_expiry(self, cred: KiteCredentialsModel):
        now = datetime.now()
        next_6_am = now.replace(hour=6, minute=0, second=0, microsecond=0)
        if now >= next_6_am:
            next_6_am += timedelta(days=1)
        ttl = int((next_6_am - now).total_seconds())
        cred.expire(ttl)

    def get_login_uri(self):
        cred = self._get_credentials_from_redis()
        return KITE_LOGIN_URL % cred.api_key

    def is_logged_in(self):
        try:
            cred = KiteCredentialsModel.get(KITE_CREDENTIALS_KEY)
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

    def _get_credentials_from_redis(self):
        try:
            return KiteCredentialsModel.get(KITE_CREDENTIALS_KEY)
        except NotFoundError:
            logger.info("Saving kite credentials in Redis")
            return KiteCredentialsModel().save()

    def _update_instances(self):
        cred = KiteCredentialsModel.get(KITE_CREDENTIALS_KEY)
        self._kite_connect = KiteConnect(cred.api_key, cred.access_token)
        self._kws = KiteTicker(cred.api_key, cred.access_token)
