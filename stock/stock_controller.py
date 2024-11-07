import asyncio
import logging

from fastapi import APIRouter
from starlette.websockets import WebSocketDisconnect
from websocket import WebSocket

from setting import SUPPORTED_STOCKS

router = APIRouter(prefix="/stocks")
logger = logging.getLogger(__name__)


@router.get("/expiries")
def get_all_stocks():
    for stock in SUPPORTED_STOCKS:
        info_service.get_stock_info(stock)
        pass


@router.post("/{stock}/expiries/{expiry}")
def set_stock_and_expiry(stock: str, expiry: str):
    quote_service.add_stock(stock)
    quote_service.add_option(stock, expiry)
    pass


@router.websocket("/{stock}/quote/ws")
async def websocket_endpoint(stock: str, websocket: WebSocket):
    try:
        logger.info(f"Stock : {stock} client connected")
        quote_service.subscribe_stock()
        await asyncio.get_event_loop().create_future()
    except WebSocketDisconnect:
        logger.info(f"Stock : {stock} client disconnected")
