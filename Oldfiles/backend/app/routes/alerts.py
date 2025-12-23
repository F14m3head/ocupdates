from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/alerts", response_class=FileResponse)
def get_alerts():
    path = os.path.join("backend", "data", "alerts.json") # FIX USING THE RIGHT PATH ON SERVER
    return FileResponse(path, media_type="application/json")