import redis.asyncio as aioredis

from info.info_service import InfoService
from login.login_service import LoginService
from setting import STOCK_OPTION_MAPPING
from tab.tab_service import TabService
from ticker.stock_ticker_service import StockTickerService

r = aioredis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
login_service = LoginService()
info_service = InfoService(STOCK_OPTION_MAPPING, login_service)
stock_ticker_service = StockTickerService(info_service, login_service, r)
tab_service = TabService(stock_ticker_service, login_service)
