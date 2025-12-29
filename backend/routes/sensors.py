from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from config.firebase_config import get_firestore_client
from datetime import datetime
from typing import Any

router = APIRouter()

class SensorData(BaseModel):
    device_id: str
    sensor_type: str
    value: float
    unit: str
    metadata: dict[str, Any] | None = None

@router.get("/")
async def get_sensor_data(
    device_id: str | None = Query(None),
    limit: int = Query(100, le=1000)
):
    """Get sensor data, optionally filtered by device"""
    db = get_firestore_client()
    query = db.collection("sensor_data")
    
    if device_id:
        query = query.where("device_id", "==", device_id)
    
    docs = query.order_by("timestamp", direction="DESCENDING").limit(limit).stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

@router.post("/")
async def add_sensor_data(data: SensorData):
    """Add new sensor data"""
    db = get_firestore_client()
    sensor_data = data.model_dump()
    sensor_data["timestamp"] = datetime.utcnow().isoformat()
    doc_ref = db.collection("sensor_data").add(sensor_data)
    return {"id": doc_ref[1].id, **sensor_data}

@router.get("/latest/{device_id}")
async def get_latest_sensor_data(device_id: str):
    """Get latest sensor data for a device"""
    db = get_firestore_client()
    docs = (
        db.collection("sensor_data")
        .where("device_id", "==", device_id)
        .order_by("timestamp", direction="DESCENDING")
        .limit(1)
        .stream()
    )
    result = [{"id": doc.id, **doc.to_dict()} for doc in docs]
    if not result:
        raise HTTPException(status_code=404, detail="No sensor data found")
    return result[0]
