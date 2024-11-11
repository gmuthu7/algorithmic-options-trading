import logging
from datetime import datetime, date

import pandas as pd
from redis_om import NotFoundError

import singleton
from info.info_model import StockInfoModel, OptionInfoModel, InstrumentModel
from login.login_service import LoginService
from setting import STOCK_OPTION_MAPPING

logger = logging.getLogger(__name__)


class InfoService:
    def __init__(self, login_service: LoginService):
        self.login_service = login_service
        self.login_service.register_observer(self._on_login_state_change)

    def get_stock_info(self, stock: str):
        return StockInfoModel.get(stock)

    def get_option_info(self, stock: str, expiry: date):
        return OptionInfoModel.get(self._get_stock_expiry_str(stock, expiry))

    def _sync_model_with_kite(self):
        connect = self.login_service.get_kite_connect()
        instruments = connect.instruments()
        df = pd.DataFrame(instruments)
        df = df.drop(["last_price", "exchange_token", "tick_size", "exchange", "segment"], axis=1)
        df["expiry"] = pd.to_datetime(df["expiry"]).dt.date
        stock_df = df[df["instrument_type"] == "EQ"]
        option_df = df[(df["instrument_type"] == "CE") | (df["instrument_type"] == "PE")]
        for stock_trading_symbol, option_name in STOCK_OPTION_MAPPING.items():
            s_df = stock_df[stock_df["tradingsymbol"] == stock_trading_symbol]
            o_df = option_df[option_df["name"] == option_name]
            stock_instrument_token = s_df["instrument_token"].values[0]
            lot_size = o_df["lot_size"].values[0]
            expiries = o_df["expiry"].unique()
            for expiry in expiries:
                e_df = o_df[o_df["expiry"] == expiry]
                token_instrument_map = {}
                for _, row in e_df.iterrows():
                    strike = row["strike"]
                    trading_symbol = row["tradingsymbol"]
                    instrument_type = row["instrument_type"]
                    instrument_token = row["instrument_token"]
                    token_instrument_map[instrument_token] = InstrumentModel(strike=strike,
                                                                             trading_symbol=trading_symbol,
                                                                             instrument_type=instrument_type)

                option_model = OptionInfoModel(pk=self._get_stock_expiry_str(stock_trading_symbol, expiry),
                                               stock=stock_trading_symbol,
                                               expiry=expiry, instruments=token_instrument_map,
                                               timestamp=datetime.now())
                option_model.save()
                singleton.set_expiry_of_model_to_daily(option_model)
            stock_model = StockInfoModel(pk=stock_trading_symbol, stock=stock_trading_symbol,
                                         instrument_token=stock_instrument_token,
                                         expiries=expiries,
                                         lot_size=lot_size,
                                         timestamp=datetime.now())
            stock_model.save()
            singleton.set_expiry_of_model_to_daily(stock_model)
        logger.info("Synced Info Service's Model")

    def _get_stock_expiry_str(self, stock: str, expiry: date):
        return f"{stock}_{expiry}"

    def _check_if_model_in_sync(self):
        try:
            StockInfoModel.get("NIFTY 50")
        except NotFoundError:
            logger.info("Info Service's Model is not in sync")
            return False
        return True

    def _on_login_state_change(self, state: str):
        if state == "CONNECTED":
            if not self._check_if_model_in_sync():
                self._sync_model_with_kite()
        else:
            pass
