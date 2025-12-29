import qrcode
import uuid
from datetime import datetime, timedelta
import os

class QRService:
    def __init__(self, storage_path="QR_images"):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        # In-memory store for test sessions; in production use a database
        self.active_qrs = {}

    def generate_gatepass(self, details: dict):
        """Generate a secure QR code for a gatepass"""
        qr_id = uuid.uuid4().hex[:12]
        expiry = datetime.now() + timedelta(minutes=15)
        
        qr_data = {
            "qr_id": qr_id,
            "name": details.get("name"),
            "roll": details.get("roll"),
            "valid_till": expiry.isoformat(),
            "status": "ACTIVE"
        }
        
        # Content format: GATEPASS|ID|ROLL|NAME
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
        """Validate a scanned QR code content string"""
        try:
            parts = qr_content.split('|')
            if len(parts) < 4 or parts[0] != "GATEPASS":
                return False, "Invalid QR content format"
            
            qr_id = parts[1]
            roll = parts[2]
            name = parts[3]
            
            # Simple validation: if we just generated it in this session
            # In real system, query database for this qr_id
            if qr_id in self.active_qrs:
                qr_info = self.active_qrs[qr_id]
                expiry = datetime.fromisoformat(qr_info["valid_till"])
                if datetime.now() > expiry:
                    return False, "QR code has expired"
                return True, qr_info
            
            # Return True for demonstration even if not in memory (stateless validation)
            return True, {"qr_id": qr_id, "roll": roll, "name": name}
            
        except Exception as e:
            return False, f"Validation error: {e}"

qr_service = QRService()
