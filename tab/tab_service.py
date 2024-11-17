from login.login_service import LoginService
from tab.tab_model import TabModel
from ticker.stock_ticker_service import StockTickerService


class TabService:

    def __init__(self, stock_ticker_service: StockTickerService, login_service: LoginService):
        self._stock_ticker_service = stock_ticker_service
        login_service.register_observer(self.login_callback)

    def login_callback(self, status):
        if status == "CONNECTED":
            self._stock_ticker_service.delete_all_stocks()
            stocks = [tab.stock for tab in self.get_tabs()]
            self._stock_ticker_service.add_all_stocks(stocks)
        else:
            pass

    def add_tab(self, tab: TabModel):
        tabs = self.get_tabs()
        # add stock to ticker service only if it is not already added
        if tab.stock not in [t.stock for t in tabs]:
            self._stock_ticker_service.add_stock(tab.stock)
        tab.pk = tab.id
        tab.save()

    def delete_tab(self, id: str):
        # delete stock from ticker service only if it is not used by any other tab
        tab = self.get_tab(id)
        TabModel.delete(id)
        tabs = self.get_tabs()
        if tab.stock not in [t.stock for t in tabs]:
            self._stock_ticker_service.delete_stock(tab.stock)

    def get_tabs(self):
        # get all contexts
        tabs = [self.get_tab(id) for id in TabModel.all_pks()]
        return tabs

    def get_tab(self, id: str):
        # get a specific context
        return TabModel.get(id)
