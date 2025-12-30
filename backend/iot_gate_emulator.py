import cv2
import numpy as np
import time
import requests
import json
from services.face_service import face_service
from config.firebase_config import initialize_firebase, get_firestore_client
import os

# Initialize Firebase
initialize_firebase()
db = get_firestore_client()

# Backend URL for fallback or additional checks if needed
BACKEND_URL = "http://localhost:8000/api"

class GatePassEmulator:
    def __init__(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(0)  # Use laptop webcam
        self.detector = cv2.QRCodeDetector()
        
        # State management
        self.scanning_qr = True
        self.current_user = None
        self.verification_status = "READY" # READY, SCANNED, VERIFYING, GRANTED, DENIED
        self.status_color = (255, 255, 255) # White
        self.last_status_time = 0
        
    def fetch_user_data(self, reg_no):
        """Fetch user embedding from Firestore"""
        try:
            doc = db.collection('users').document(reg_no).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            print(f"Error fetching user: {e}")
        return None

    def verify_identity(self, frame, stored_embedding):
        """Compare live frame with stored embedding using FaceService"""
        try:
            # Convert frame to bytes for face_service (it normally takes bytes)
            _, img_encoded = cv2.imencode('.jpg', frame)
            face_bytes = img_encoded.tobytes()
            
            # Use the existing verify_embedding logic
            is_match = face_service.verify_embedding(face_bytes, stored_embedding)
            return is_match
        except Exception as e:
            print(f"Face verification error: {e}")
            return False

    def run(self):
        print("IoT Gate Emulator Started. Waiting for QR Code...")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Mirror the frame for more natural display
            frame = cv2.flip(frame, 1)
            display_frame = frame.copy()

            # 1. QR Code Detection Loop
            if self.scanning_qr:
                data, bbox, _ = self.detector.detectAndDecode(frame)
                
                if data:
                    print(f"QR Detected: {data}")
                    try:
                        # QR might be a JSON string or just a reg_no
                        # In our app, it contains pass_id or similar. 
                        # Let's assume it has the reg_no or we fetch by pass_id
                        qr_payload = {}
                        try:
                            qr_payload = json.loads(data)
                            reg_no = qr_payload.get('reg_no')
                        except:
                            reg_no = data # Fallback to raw text

                        if reg_no:
                            self.verification_status = "QR SCANNED. VERIFYING FACE..."
                            self.status_color = (255, 165, 0) # Orange
                            
                            # 2. Fetch User Data
                            user_data = self.fetch_user_data(reg_no)
                            if user_data and 'face_embedding' in user_data:
                                stored_embedding = user_data['face_embedding']
                                
                                # 3. Perform Face Recognition
                                match = self.verify_identity(frame, stored_embedding)
                                
                                if match:
                                    self.verification_status = f"ACCESS GRANTED: {reg_no}"
                                    self.status_color = (0, 255, 0) # Green
                                else:
                                    self.verification_status = "ACCESS DENIED: FACE MISMATCH"
                                    self.status_color = (0, 0, 255) # Red
                            else:
                                self.verification_status = "ACCESS DENIED: UNKNOWN USER"
                                self.status_color = (0, 0, 255)
                            
                            self.scanning_qr = False
                            self.last_status_time = time.time()
                    except Exception as e:
                        print(f"Process error: {e}")

            # 4. Draw UI Overlays
            # Draw Status Header
            cv2.rectangle(display_frame, (0, 0), (display_frame.shape[1], 60), (0, 0, 0), -1)
            cv2.putText(display_frame, self.verification_status, (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.status_color, 2)

            # If scanning, show a box in middle
            if self.scanning_qr:
                h, w, _ = display_frame.shape
                cv2.rectangle(display_frame, (w//4, h//4), (3*w//4, 3*h//4), (255, 255, 255), 2)
                cv2.putText(display_frame, "Place QR Code Here", (w//4, h//4 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Reset scanning after 5 seconds of status display
            if not self.scanning_qr and (time.time() - self.last_status_time > 5):
                self.scanning_qr = True
                self.verification_status = "READY"
                self.status_color = (255, 255, 255)

            # Show window
            cv2.imshow("IoT Gate Security Emulator", display_frame)

            # Break on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    emulator = GatePassEmulator()
    emulator.run()
