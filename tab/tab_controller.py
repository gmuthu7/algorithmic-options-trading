import logging

from fastapi import APIRouter

from singleton import tab_service
from tab.tab_model import TabModel, TabModelPydantic

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/tabs")
def tabs():
    return tab_service.get_tabs()


@router.post("/tab")
def add_tab(tab: TabModelPydantic):
    tab = TabModel(**tab.dict())
    tab_service.add_tab(tab)
    return {"status": "success"}


@router.delete("/tab/{tab_id}")
def add_tab(tab_id: str):
    tab_service.delete_tab(tab_id)
    return {"status": "success"}

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
