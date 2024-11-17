import logging

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from setting import STOCK_STREAM_KEY
from singleton import tab_service, r

router = APIRouter()

logger = logging.getLogger(__name__)


@router.websocket("/tab/{tab_id}/stock/tick/ws")
async def stock_ltp(tab_id: str, websocket: WebSocket):
    await websocket.accept()
    tab = tab_service.get_tab(tab_id)
    logger.info(f"{tab.stock} ltp client connected")
    try:
        latest_entry = await r.xrevrange(f"{STOCK_STREAM_KEY}:{tab.stock}", count=1)
        if latest_entry:
            _, data = latest_entry[0]
            await websocket.send_json(data)
        while True:
            response = await r.xread({f"{STOCK_STREAM_KEY}:{tab.stock}": "$"}, block=0, count=1)
            if response:
                _, messages = response[0]
                _, data = messages[0]
                await websocket.send_json(data)
    except WebSocketDisconnect:
        logger.info(f"{tab.stock} ltp client disconnected")
