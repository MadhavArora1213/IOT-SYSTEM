from pyzbar.pyzbar import decode
import cv2

class QRScanner:
    def __init__(self):
        pass

    def scan(self, frame):
        """Detect and decode QR code from a frame"""
        qr_codes = decode(frame)
        if qr_codes:
            # Return the first detected QR code data
            return qr_codes[0].data.decode('utf-8')
        return None
