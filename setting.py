import logging

import pandas as pd
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s.%(msecs)03d %(name)s:%(funcName)s - %(processName)s:%(thread)s -%(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
pd.set_option("display.max_column", None)
KITE_LOGIN_URL = "https://kite.zerodha.com/connect/login?api_key=%s&v=3"
KITE_CREDENTIALS_KEY = "kite_credentials"
STOCK_STREAM_KEY = "ltp:stock"
DAILY_TTL_HOUR = 6
TICKER_THREADED = True
STOCK_OPTION_MAPPING = {
    "NIFTY 50": "NIFTY",
    "NIFTY FIN SERVICE": "FINNIFTY",
    "NIFTY BANK": "BANKNIFTY",
    "NIFTY MID SELECT": "MIDCPNIFTY",
    "SENSEX": "SENSEX"
}  # stock_tradingsymbol : option_name
# If you modify this mapping, you will have to update info_model again using info_service
