import qrcode
import uuid
from datetime import datetime, timedelta
import os
from pyzbar.pyzbar import decode
from PIL import Image
import io

class QRService:
    def __init__(self, storage_path="QR_images"):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        # In a real app, this would be a database
        self.active_qrs = {}

    def generate_gatepass(self, details: dict):
        """Generate a QR code for a gatepass"""
        qr_id = uuid.uuid4().hex[:12]
        expiry = datetime.now() + timedelta(minutes=15)
        
        qr_data = {
            "qr_id": qr_id,
            "name": details.get("name"),
            "roll": details.get("roll"),
            "valid_till": expiry.isoformat(),
            "status": "ACTIVE"
        }
        
        # Simple string representation for the QR content
        qr_content = f"GATEPASS|{qr_id}|{details.get('roll')}|{details.get('name')}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        file_path = os.path.join(self.storage_path, f"QR_{qr_id}.png")
        img.save(file_path)
        
        self.active_qrs[qr_id] = {**qr_data, "file_path": file_path}
        return self.active_qrs[qr_id]

    def validate_qr(self, qr_content: str):
        """Validate a scanned QR code content"""
        try:
            parts = qr_content.split('|')
            if len(parts) < 4 or parts[0] != "GATEPASS":
                return False, "Invalid QR format"
            
            qr_id = parts[1]
            # Check if QR exists in our "database"
            if qr_id not in self.active_qrs:
                return False, "QR code not registered"
            
            qr_info = self.active_qrs[qr_id]
            expiry = datetime.fromisoformat(qr_info["valid_till"])
            
            if datetime.now() > expiry:
                return False, "QR code expired"
            
            return True, qr_info
        except Exception as e:
            return False, str(e)

qr_service = QRService()
