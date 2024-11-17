from fastapi import APIRouter

from singleton import login_service

router = APIRouter()


@router.get("/profile")
def profile():
    return login_service.get_kite_connect().profile()
