from fastapi import APIRouter, HTTPException
from starlette.responses import RedirectResponse

from singleton import login_service

router = APIRouter(prefix="/kite")


@router.get("/profile")
def profile():
    if login_service.is_logged_in():
        return login_service.get_kite_connect().profile()
    else:
        raise HTTPException(status_code=401, detail="Not logged in")


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
