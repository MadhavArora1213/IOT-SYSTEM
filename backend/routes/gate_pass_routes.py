from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from config.firebase_config import get_firestore_client
from services.qr_service import qr_service
from datetime import datetime
import os
import shutil
import uuid

router = APIRouter()

PROOF_STORAGE_PATH = "Storage/Proofs"
os.makedirs(PROOF_STORAGE_PATH, exist_ok=True)

@router.post("/request")
async def request_gate_pass(
    reg_no: str = Form(...),
    purpose: str = Form(...),
    leave_time: str = Form(...),
    return_time: str = Form(...),
    proof: UploadFile = File(...)
):
    """
    Request a gate pass.
    1. Validate User.
    2. Save Proof document.
    3. Create Gate Pass entry (Auto-Approved).
    4. Generate and return QR Code content (or URL).
    """
    db = get_firestore_client()
    
    # 1. Verify User exists
    user_doc = db.collection('users').document(reg_no).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user_doc.to_dict()
    
    # 2. Save Proof
    try:
        file_ext = proof.filename.split(".")[-1]
        proof_filename = f"proof_{reg_no}_{uuid.uuid4()}.{file_ext}"
        proof_path = os.path.join(PROOF_STORAGE_PATH, proof_filename)
        
        with open(proof_path, "wb") as buffer:
            shutil.copyfileobj(proof.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save proof: {str(e)}")

    # 3. Create Gate Pass Record
    pass_id = str(uuid.uuid4())
    gate_pass_data = {
        "pass_id": pass_id,
        "reg_no": reg_no,
        "name": user_data.get("email", "Unknown"), 
        "class": user_data.get("class", "N/A"),
        "department": user_data.get("department", "N/A"),
        "profile_image": user_data.get("image_filename"),
        "purpose": purpose,
        "leave_time": leave_time,
        "return_time": return_time,
        "proof_path": proof_path,
        "proof_filename": proof_filename,
        "status": "APPROVED",
        "created_at": datetime.now().isoformat()
    }
    
    # Generate QR Content (Simple JSON for now)
    qr_data = {
        "pass_id": pass_id,
        "reg_no": reg_no,
        "status": "APPROVED",
        "valid_until": return_time
    }
    
    # Save to Firestore
    try:
        db.collection('gate_passes').document(pass_id).set(gate_pass_data)
        
        # Also generate visual QR code and save it (optional, but good for display)
        qr_image_path = qr_service.generate_gatepass(qr_data) # Reusing existing service
        
        # Update record with QR path
        db.collection('gate_passes').document(pass_id).update({
            "qr_code_path": qr_image_path
        })
        
        return {
            "status": "success",
            "message": "Gate Pass Approved",
            "pass_data": gate_pass_data,
            "qr_code_path": qr_image_path
        }
        
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/my-passes/{reg_no}")
async def get_my_passes(reg_no: str):
    """Get all gate passes for a user"""
    db = get_firestore_client()
    try:
        # Check without order_by first to see if it's an indexing issue
        docs = db.collection('gate_passes').where('reg_no', '==', reg_no).stream()
        
        passes = []
        for doc in docs:
            data = doc.to_dict()
            passes.append(data)
        
        # Sort in memory for now to avoid indexing requirement
        passes.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
        return {"status": "success", "data": passes}
    except Exception as e:
        print(f"Firestore Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
