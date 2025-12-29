import cv2
import os
import sys

# Check for keyboard module or use alternative
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("⚠️ 'keyboard' module not installed. Using OpenCV key detection instead.")
    print("   To install: pip install keyboard")

# Create necessary folders
os.makedirs('faces', exist_ok=True)

# Get user name
name = input("Enter your name: ").strip()
if not name:
    print("❌ Name cannot be empty!")
    sys.exit()

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Webcam not found.")
    sys.exit()

print("\n" + "="*50)
print("📸 FACE CAPTURE INSTRUCTIONS:")
print("="*50)
print("1. Face the webcam directly")
print("2. Ensure good lighting")
print("3. Keep a neutral expression")
print("4. Press SPACE to capture")
print("5. Press ESC to cancel")
print("="*50)

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture frame")
        break
    
    # Display instructions on frame
    height, width = frame.shape[:2]
    cv2.putText(frame, "Press SPACE to Capture", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, "Press ESC to Cancel", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(frame, f"Name: {name}", (10, height - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imshow("Capture Face - " + name, frame)
    
    # Key detection
    if KEYBOARD_AVAILABLE:
        # Check if window is focused before using keyboard module to avoid global hijacking if possible
        # but keyboard.is_pressed is global. We'll stick to provided logic but add fallback.
        try:
            if keyboard.is_pressed('esc'):
                print("🚪 Exiting without saving.")
                break
            elif keyboard.is_pressed('space'):
                # Save the image
                img_path = f"faces/{name}.jpg"
                cv2.imwrite(img_path, frame)
                print(f"✅ Face saved as: {img_path}")
                
                # Show confirmation
                cv2.putText(frame, "CAPTURED!", (width//2 - 100, height//2), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                cv2.imshow("Capture Face - " + name, frame)
                cv2.waitKey(1000)
                break
        except:
            KEYBOARD_AVAILABLE = False # Fallback to OpenCV if keyboard fails (e.g. permission)
            
    if not KEYBOARD_AVAILABLE:
        # Alternative using OpenCV
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            print("🚪 Exiting without saving.")
            break
        elif key == 32:  # SPACE
            # Save the image
            img_path = f"faces/{name}.jpg"
            cv2.imwrite(img_path, frame)
            print(f"✅ Face saved as: {img_path}")
            
            # Show confirmation
            cv2.putText(frame, "CAPTURED!", (width//2 - 100, height//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            cv2.imshow("Capture Face - " + name, frame)
            cv2.waitKey(1000)
            break

cap.release()
cv2.destroyAllWindows()
