from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.qr_service import qr_service
from services.face_service import face_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/verify")
async def verify_gatepass(
    qr_content: str = Form(...),
    face_image: UploadFile = File(...)
):
    """
    Endpoint for IoT device to verify access.
    1. Validates QR code.
    2. Matches captured face against registered face for the user.
    """
    # 1. Validate QR
    is_valid_qr, qr_info_or_error = qr_service.validate_qr(qr_content)
    if not is_valid_qr:
        return {
            "status": "FAIL",
            "reason": "QR_INVALID",
            "message": qr_info_or_error
        }
    
    qr_info = qr_info_or_error
    user_roll = qr_info["roll"]
    user_name = qr_info["name"]
    
    # 2. Capture face image bytes
    face_bytes = await face_image.read()
    
    # 3. Verify Face
    # In this system, we expect the face to be registered under the user's name or roll
    # Let's use roll as the identifier for embeddings if possible, or name as per user script
    is_valid_face, score_or_reason = face_service.verify_face(face_bytes, user_name)
    
    if is_valid_face:
        logger.info(f"Access GRANTED for {user_name} ({user_roll})")
        return {
            "status": "SUCCESS",
            "user": user_name,
            "roll": user_roll,
            "confidence": f"{1 - score_or_reason:.2f}" if isinstance(score_or_reason, float) else "N/A"
        }
    else:
        logger.warning(f"Access DENIED for {user_name} ({user_roll}): {score_or_reason}")
        return {
            "status": "FAIL",
            "reason": "FACE_MISMATCH",
            "message": str(score_or_reason),
            "user": user_name
        }

@router.post("/register-qr")
async def register_qr(name: str = Form(...), roll: str = Form(...)):
    """Helper endpoint to generate and register a QR for testing"""
    details = {"name": name, "roll": roll}
    result = qr_service.generate_gatepass(details)
    return result
