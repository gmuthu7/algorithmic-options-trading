import logging

from fastapi import APIRouter

from setting import STOCK_OPTION_MAPPING
from singleton import info_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/tab/{tab_id}/stock/ws")
def stocks(tab_id: str):
    stock_expiry_mapping = {}
    for stock in STOCK_OPTION_MAPPING:
        info = info_service.get_stock_info(stock)
        stock_expiry_mapping[stock] = info.expiries
    return stock_expiry_mapping
