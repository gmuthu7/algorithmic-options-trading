import logging

from fastapi import APIRouter

from setting import STOCK_OPTION_MAPPING
from singleton import info_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stocks")
def stocks():
    stock_expiry_mapping = {}
    for stock in STOCK_OPTION_MAPPING:
        info = info_service.get_stock_info(stock)
        stock_expiry_mapping[stock] = info.expiries
    return stock_expiry_mapping


@router.get("/contexts")
def contexts():
    pass
# @router.post("/{stock}/expiries/{expiry}")
# def set_stock_and_expiry(stock: str, expiry: str):
#     quote_service.add_stock(stock)
#     quote_service.add_option(stock, expiry)
#     pass
#
#
# @router.websocket("/{stock}/quote/ws")
# async def websocket_endpoint(stock: str, websocket: WebSocket):
#     try:
#         logger.info(f"Stock : {stock} client connected")
#         quote_service.subscribe_stock()
#         await asyncio.get_event_loop().create_future()
#     except WebSocketDisconnect:
#         logger.info(f"Stock : {stock} client disconnected")
