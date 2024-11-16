from info.info_service import InfoService
from login.login_service import LoginService
from setting import STOCK_OPTION_MAPPING
from tab.tab_service import TabService

login_service = LoginService()
info_service = InfoService(STOCK_OPTION_MAPPING, login_service)
tab_service = TabService()
