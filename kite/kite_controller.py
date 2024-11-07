from fastapi import APIRouter

from singleton import kite_instance_service

router = APIRouter(prefix="/kite")


@router.get("/access_token")
def request_token(status: str, request_token: str):
    if status != "success":
        raise Exception("Login failed")
    kite_instance_service.set_request_token(request_token)
    return "Kite access token generated and set successfully"
