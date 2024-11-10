from typing import Optional

from fastapi import APIRouter
from starlette.responses import RedirectResponse

from setting import AOT_UI_APP_URL
from singleton import kite_login_service

router = APIRouter(prefix="/kite")


@router.get("/profile")
def profile():
    if kite_login_service.is_logged_in():
        return {"logged_in": True, "profile": kite_login_service.get_kite_connect().profile()}
    else:
        return {"logged_in": False}


@router.get("/login")
def request_token(status: Optional[str] = None, request_token: Optional[str] = None):
    if status != "success":
        return RedirectResponse(kite_login_service.get_login_uri())
    kite_login_service.set_request_token(request_token)
    return RedirectResponse(f"{AOT_UI_APP_URL}/app")
