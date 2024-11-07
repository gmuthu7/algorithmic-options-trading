import logging

import pandas as pd
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s.%(msecs)03d %(name)s:%(funcName)s - %(processName)s:%(thread)s -%(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
pd.set_option("display.max_column", None)
KITE_LOGIN_URL = "https://kite.zerodha.com/connect/login?api_key=%s&v=3"
KITE_ACCESS_TOKEN_TTL = 12 * 60 * 60  # 12 hours
KITE_CREDENTIALS_KEY = "kite_credentials"
KITE_INFO_TTL = 7 * 24 * 60 * 60  # 10 days
KITE_TICKER_THREADED = False
KITE_STOCK_OPTION_MAPPING = {
    "NIFTY 50": "NIFTY",
    "NIFTY FIN SERVICE": "FINNIFTY",
    "NIFTY BANK": "BANKNIFTY",
    "NIFTY MID SELECT": "MIDCPNIFTY",
    "SENSEX": "SENSEX"
}  # stock_tradingsymbol : option_name
