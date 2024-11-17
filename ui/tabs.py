import logging

from fastapi import APIRouter

from singleton import tab_service, stock_ticker_service
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
