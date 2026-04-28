from fastapi import APIRouter
from backend.services.farm_service import run_garden_service, get_status

router = APIRouter()


@router.post("/garden")
def run_garden(pid: int, cid: int = 10):
    return run_garden_service(pid, cid)


@router.get("/status")
def status():
    return get_status()