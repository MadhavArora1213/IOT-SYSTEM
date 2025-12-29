import cv2
import logging

class Camera:
    def __init__(self, device_id=0):
        self.cap = cv2.VideoCapture(device_id)
        if not self.cap.isOpened():
            logging.error("Could not open camera device")

    def capture_frame(self):
        """Capture a single frame from the camera"""
        ret, frame = self.cap.read()
        if not ret:
            logging.error("Failed to capture frame")
            return None
        return frame

    def release(self):
        self.cap.release()
