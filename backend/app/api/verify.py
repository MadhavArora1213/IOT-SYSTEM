from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..services.qr_service import qr_service
from ..services.face_service import face_service
from ..database import db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/verify")
async def verify_gatepass(
    qr_content: str = Form(...),
    face_image: UploadFile = File(...)
):
    """
    Receives user ID (from QR) and face image, validates QR code, 
    performs face recognition, and returns decision.
    """
    # 1. Validate QR
    is_valid_qr, qr_info_or_error = qr_service.validate_qr(qr_content)
    if not is_valid_qr:
        db.log_event("VERIFY_FAIL", {"reason": "QR_INVALID", "content": qr_content})
        return {
            "status": "FAIL",
            "reason": "QR_INVALID",
            "message": qr_info_or_error
        }
    
    qr_info = qr_info_or_error
    user_roll = qr_info.get("roll")
    user_name = qr_info.get("name")
    
    # 2. Capture face image bytes
    face_bytes = await face_image.read()
    
    # 3. Verify Face
    is_valid_face, score_or_reason = face_service.verify_face(face_bytes, user_name)
    
    if is_valid_face:
        db.log_event("VERIFY_SUCCESS", {"user": user_name, "roll": user_roll})
        return {
            "status": "SUCCESS",
            "user": user_name,
            "roll": user_roll,
            "message": "Access Granted",
            "confidence": f"{1 - score_or_reason:.2f}" if isinstance(score_or_reason, float) else "N/A"
        }
    else:
        db.log_event("VERIFY_FAIL", {"user": user_name, "reason": "FACE_MISMATCH"})
        return {
            "status": "FAIL",
            "reason": "FACE_MISMATCH",
            "message": "Face verification failed",
            "user": user_name
        }

@router.post("/register-qr")
async def register_qr(
    name: str = Form(...), 
    roll: str = Form(...),
    registration_image: UploadFile = File(None)
):
    """
    Endpoint to generate a gatepass and optionally save a registration photo.
    """
    # 1. Save registration face if provided
    if registration_image:
        face_bytes = await registration_image.read()
        # Use roll as the unique identifier for faces
        face_service.save_registration_face(roll, face_bytes)
    
    # 2. Generate QR
    details = {"name": name, "roll": roll}
    result = qr_service.generate_gatepass(details)
    return result
