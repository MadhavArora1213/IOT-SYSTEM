import requests
import cv2

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def verify_access(self, qr_content, face_frame):
        """Send verification request to backend"""
        try:
            # Encode face frame as JPG
            _, img_encoded = cv2.imencode('.jpg', face_frame)
            face_bytes = img_encoded.tobytes()

            files = {'face_image': ('face.jpg', face_bytes, 'image/jpeg')}
            data = {'qr_content': qr_content}
            
            response = requests.post(f"{self.base_url}/verify", data=data, files=files)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "FAIL", "message": f"Server Error: {response.status_code}"}
        except Exception as e:
            return {"status": "FAIL", "message": f"Connection Error: {str(e)}"}
