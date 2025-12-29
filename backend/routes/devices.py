from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config.firebase_config import get_firestore_client
from datetime import datetime

router = APIRouter()

class Device(BaseModel):
    name: str
    type: str
    location: str | None = None
    status: str = "inactive"

class DeviceUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    location: str | None = None
    status: str | None = None

@router.get("/")
async def get_all_devices():
    """Get all devices"""
    db = get_firestore_client()
    devices_ref = db.collection("devices")
    docs = devices_ref.stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

@router.get("/{device_id}")
async def get_device(device_id: str):
    """Get a specific device"""
    db = get_firestore_client()
    doc = db.collection("devices").document(device_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"id": doc.id, **doc.to_dict()}

@router.post("/")
async def create_device(device: Device):
    """Create a new device"""
    db = get_firestore_client()
    device_data = device.model_dump()
    device_data["created_at"] = datetime.utcnow().isoformat()
    doc_ref = db.collection("devices").add(device_data)
    return {"id": doc_ref[1].id, **device_data}

@router.put("/{device_id}")
async def update_device(device_id: str, device: DeviceUpdate):
    """Update a device"""
    db = get_firestore_client()
    doc_ref = db.collection("devices").document(device_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Device not found")
    update_data = {k: v for k, v in device.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    doc_ref.update(update_data)
    return {"id": device_id, **update_data}

@router.delete("/{device_id}")
async def delete_device(device_id: str):
    """Delete a device"""
    db = get_firestore_client()
    doc_ref = db.collection("devices").document(device_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Device not found")
    doc_ref.delete()
    return {"message": "Device deleted successfully"}
