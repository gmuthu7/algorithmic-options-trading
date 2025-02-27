from fastapi import APIRouter
from starlette.responses import RedirectResponse

from singleton import login_service

router = APIRouter()


@router.get("/login/status")
def login_status():
    if login_service.is_logged_in():
        return {"status": True}
    else:
        return {"status": False}


@router.get("/login")
def login(redirect_uri: str):
    if login_service.is_logged_in():
        return RedirectResponse(redirect_uri)
    else:
        return RedirectResponse(login_service.get_login_uri() + f"&redirect_params=redirect_uri={redirect_uri}")


@router.get("/verify_login")
def verify_login(status: str, request_token: str, redirect_uri: str):
    if status != "success":
        return RedirectResponse(login_service.get_login_uri())
    login_service.set_request_token(request_token)
    return RedirectResponse(f"{redirect_uri}")
