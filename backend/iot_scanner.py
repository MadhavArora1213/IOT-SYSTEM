import cv2
import numpy as np
import torch
from services.face_service import face_service
from config.firebase_config import initialize_firebase, get_firestore_client
import time
import json

# Initialize Firebase
initialize_firebase()
db = get_firestore_client()

class GateScanner:
    def __init__(self):
        self.cap = cv2.VideoCapture(0) # Use laptop webcam
        self.qr_detector = cv2.QRCodeDetector()
        
        self.known_users = [] # List of {reg_no: str, embedding: np.array, name: str}
        self.load_users()
        
        self.state = "SCAN_FACE" # SCAN_FACE -> SCAN_QR -> VERIFIED
        self.detected_user = None
        self.last_face_check = 0
        self.message = "Initializing..."
        self.message_color = (255, 255, 255)

    def load_users(self):
        print("Fetching registered users for local recognition...")
        users_ref = db.collection('users').stream()
        for doc in users_ref:
            data = doc.to_dict()
            if 'face_embedding' in data and data['face_embedding']:
                self.known_users.append({
                    "reg_no": data.get('reg_no'),
                    "name": data.get('email', 'Unknown'),
                    "embedding": np.array(data['face_embedding'])
                })
        print(f"Loaded {len(self.known_users)} users with face data.")

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # UI Overlays
            cv2.putText(frame, f"STATUS: {self.state}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, self.message, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.message_color, 2)

            if self.state == "SCAN_FACE":
                self.handle_face_scan(frame)
            elif self.state == "SCAN_QR":
                self.handle_qr_scan(frame)
            elif self.state == "VERIFIED":
                self.handle_verified_state(frame)

            cv2.imshow("Gate Scanner (Simulating Pi)", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'): # Reset state manually
                self.reset()

        self.cap.release()
        cv2.destroyAllWindows()

    def handle_face_scan(self, frame):
        self.message = "Please align your face to the camera"
        self.message_color = (255, 255, 255)
        
        # Recognition every 2 seconds to avoid lag
        if time.time() - self.last_face_check > 2.0:
            self.last_face_check = time.time()
            
            # Convert frame to bytes for face_service
            _, buffer = cv2.imencode('.jpg', frame)
            face_bytes = buffer.tobytes()
            
            embedding = face_service.get_embedding(face_bytes)
            if embedding is not None:
                # Compare against all known users
                best_match = None
                min_dist = 1.0
                
                for user in self.known_users:
                    dist = np.linalg.norm(embedding.flatten() - user['embedding'].flatten()) # L2 or use cosine from service
                    # Using Euclidean or Cosine distance. face_service uses Cosine < 0.6
                    # Let's use the actual cosine from service logic
                    from scipy.spatial.distance import cosine
                    dist = cosine(embedding.flatten(), user['embedding'].flatten())
                    
                    if dist < min_dist:
                        min_dist = dist
                        best_match = user
                
                if best_match and min_dist < 0.6:
                    self.detected_user = best_match
                    self.state = "SCAN_QR"
                    self.message = f"Face Matched: {best_match['name']}. Scan your QR now!"
                    self.message_color = (0, 255, 0)
                    print(f"Match found: {best_match['reg_no']} (Dist: {min_dist})")

    def handle_qr_scan(self, frame):
        data, bbox, _ = self.qr_detector.detectAndDecode(frame)
        
        if data:
            try:
                # The mobile app pass_id is usually in the QR. 
                # Our /request returns a pass_id.
                # Let's check if the QR matches the detected user's reg_no.
                # In index.tsx/two.tsx we used `pass_id` in QR.
                
                # Fetch pass from firestore
                pass_doc = db.collection('gate_passes').document(data).get()
                if pass_doc.exists:
                    pass_info = pass_doc.to_dict()
                    if pass_info['reg_no'] == self.detected_user['reg_no']:
                        self.state = "VERIFIED"
                        self.verified_time = time.time()
                        self.message = "VERIFIED! Access Granted."
                        self.message_color = (0, 255, 0)
                    else:
                        self.message = "QR Mismatch! Identity Theft?"
                        self.message_color = (0, 0, 255)
                else:
                    # Maybe the QR contains plain reg_no (fallback/test)
                    if data == self.detected_user['reg_no']:
                        self.state = "VERIFIED"
                        self.verified_time = time.time()
                        self.message = "VERIFIED! (Dev Mode)"
                        self.message_color = (0, 255, 0)
                    else:
                        self.message = "Invalid QR Code"
                        self.message_color = (0, 0, 255)
            except Exception as e:
                print(f"QR Error: {e}")

    def handle_verified_state(self, frame):
        if time.time() - self.verified_time > 5.0:
            self.reset()
            
    def reset(self):
        self.state = "SCAN_FACE"
        self.detected_user = None
        self.message = "Waiting for next user..."
        self.message_color = (255, 255, 255)

if __name__ == "__main__":
    scanner = GateScanner()
    scanner.run()
