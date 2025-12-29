import cv2
import time
import logging
from camera import Camera
from qr_scanner import QRScanner
from api_client import APIClient
from gpio_control import GPIOControl
from voice import VoiceFeedback
import config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Initialize components
    cam = Camera(config.CAMERA_ID)
    qr_scanner = QRScanner()
    api = APIClient(config.BACKEND_URL)
    gpio = GPIOControl()
    voice = VoiceFeedback()

    logging.info("Smart Gate Pass Terminal - Edge Controller Active")
    voice.speak("System ready. Please show your QR code.")

    try:
        while True:
            frame = cam.capture_frame()
            if frame is None:
                continue

            # 1. Look for QR Code
            qr_content = qr_scanner.scan(frame)
            if qr_content:
                logging.info(f"QR Scanned: {qr_content}")
                voice.speak("QR detected. Holding for face capture.")
                
                # Visual feedback on frame
                cv2.putText(frame, "SCANNED! Processing...", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("Smart Gate Pass Terminal", frame)
                cv2.waitKey(1000)

                # 2. Re-capture frame for face (better quality/pose)
                face_frame = cam.capture_frame()
                
                # 3. Verify with Backend
                logging.info("Verifying identity...")
                result = api.verify_access(qr_content, face_frame)

                if result.get("status") == "SUCCESS":
                    user = result.get("user", "User")
                    logging.info(f"Access Granted: {user}")
                    gpio.access_granted()
                    voice.speak(f"Access Granted. Welcome {user}.")
                else:
                    reason = result.get("message", "Unknown error")
                    logging.warning(f"Access Denied: {reason}")
                    gpio.access_denied()
                    voice.speak("Access Denied.")

                # Hold feedback state
                time.sleep(3)
                gpio.reset()
                logging.info("Ready for next scan")
                voice.speak("Ready.")

            # Display preview
            cv2.imshow("Smart Gate Pass Terminal", frame)
            
            if cv2.waitKey(1) & 0xFF == 27: # ESC
                break

    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
