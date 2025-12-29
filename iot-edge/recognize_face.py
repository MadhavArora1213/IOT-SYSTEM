import cv2
import torch
import numpy as np
import os
import time
from pathlib import Path
import sys

def check_dependencies():
    """Check if required modules are installed"""
    try:
        from facenet_pytorch import MTCNN, InceptionResnetV1
        from scipy.spatial.distance import cosine
        from PIL import Image
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n📦 Install with: pip install facenet-pytorch scipy pillow")
        return False

def load_embeddings():
    """Load all registered face embeddings"""
    embeddings = {}
    names = []
    
    if not os.path.exists('embeddings'):
        print("❌ 'embeddings/' folder not found!")
        print("📁 Please run 'register_face.py' first.")
        return None, None
    
    embedding_files = [f for f in os.listdir('embeddings') if f.endswith('_embedding.npy')]
    
    if not embedding_files:
        print("❌ No registered faces found!")
        print("📁 Please run 'register_face.py' first.")
        return None, None
    
    print(f"📂 Loading {len(embedding_files)} registered face(s)...")
    
    for file in embedding_files:
        try:
            name = file.replace('_embedding.npy', '')
            embedding = np.load(os.path.join('embeddings', file))
            
            # Ensure embedding is normalized
            embedding = embedding / np.linalg.norm(embedding)
            embeddings[name] = embedding
            names.append(name)
            
            print(f"   ✅ {name}")
        except Exception as e:
            print(f"   ❌ Error loading {file}: {e}")
    
    return embeddings, names

def setup_models(device):
    """Initialize face detection and recognition models"""
    try:
        from facenet_pytorch import MTCNN, InceptionResnetV1
        
        print("🔄 Loading face detection model...")
        mtcnn = MTCNN(
            image_size=160,
            margin=20,
            min_face_size=40,
            thresholds=[0.6, 0.7, 0.7],
            factor=0.709,
            post_process=True,
            device=device,
            keep_all=False  # Detect only one face for simplicity
        )
        
        print("🔄 Loading face recognition model...")
        model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
        
        return mtcnn, model
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return None, None

def recognize_face(face_pil, model, embeddings, device):
    """Recognize a face from PIL image"""
    from scipy.spatial.distance import cosine
    
    try:
        # Convert face to tensor and get embedding
        with torch.no_grad():
            face_tensor = face_pil.unsqueeze(0).to(device)
            embedding = model(face_tensor).detach().cpu().numpy()
        
        # Normalize embedding
        embedding = embedding / np.linalg.norm(embedding)
        
        # Compare with registered faces
        best_match = None
        min_distance = float('inf')
        
        for name, registered_embedding in embeddings.items():
            distance = cosine(embedding.flatten(), registered_embedding.flatten())
            if distance < min_distance:
                min_distance = distance
                best_match = name
        
        # Threshold for recognition (adjust as needed)
        if min_distance < 0.6:  # Lower = stricter
            return best_match, min_distance
        else:
            return "Unknown", min_distance
            
    except Exception as e:
        print(f"⚠️ Recognition error: {e}")
        return "Error", 1.0

def draw_info(frame, face_info, fps):
    """Draw information on frame"""
    height, width = frame.shape[:2]
    
    # Draw semi-transparent overlay for text
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width, 70), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
    
    # Draw FPS
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Draw recognition result
    if face_info:
        name, distance, (x1, y1, x2, y2) = face_info
        
        # Draw face bounding box
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw name and confidence
        label = f"{name} ({distance:.3f})"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        
        # Background for label
        cv2.rectangle(frame, (x1, y1 - 30), (x1 + label_size[0] + 10, y1), color, -1)
        cv2.putText(frame, label, (x1 + 5, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    else:
        cv2.putText(frame, "No face detected", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # Draw instructions
    cv2.putText(frame, "Press ESC to exit", (width - 200, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

def main():
    print("\n" + "="*60)
    print("👁️  REAL-TIME FACE RECOGNITION")
    print("="*60)
    
    if not check_dependencies():
        return
    
    # Load embeddings
    embeddings, names = load_embeddings()
    if not embeddings:
        input("\nPress Enter to exit...")
        return
    
    print(f"\n👤 Registered: {', '.join(names)}")
    
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"📊 Using device: {device}")
    
    # Setup models
    mtcnn, model = setup_models(device)
    if not mtcnn or not model:
        return
    
    # Open webcam
    print("\n🎥 Opening webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open webcam!")
        return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("\n✅ Recognition started!")
    print("📋 Instructions:")
    print("   • Look directly at the camera")
    print("   • Ensure good lighting")
    print("   • Press ESC to exit")
    print("\n" + "-"*60)
    
    # For FPS calculation
    frame_count = 0
    start_time = time.time()
    fps = 0
    
    # Skip frames for performance (process every nth frame)
    skip_frames = 2
    frame_counter = 0
    
    # For face tracking (simple implementation)
    last_face_info = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break
        
        frame_counter += 1
        
        # Calculate FPS
        frame_count += 1
        if frame_count % 30 == 0:
            elapsed = time.time() - start_time
            fps = 30 / elapsed
            start_time = time.time()
        
        face_info = None
        
        # Process face every 'skip_frames' frames
        if frame_counter % skip_frames == 0:
            try:
                from PIL import Image
                
                # Convert to RGB for MTCNN
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect face
                boxes, probs = mtcnn.detect(rgb_frame)
                
                if boxes is not None and len(boxes) > 0:
                    # Get the first face (most prominent)
                    box = boxes[0]
                    prob = probs[0]
                    
                    if prob > 0.9:  # Confidence threshold
                        x1, y1, x2, y2 = [int(coord) for coord in box]
                        
                        # Ensure coordinates are within frame
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                        
                        # Extract face region
                        face_rgb = rgb_frame[y1:y2, x1:x2]
                        
                        if face_rgb.size > 0:
                            # Convert to PIL Image
                            face_pil = Image.fromarray(face_rgb)
                            
                            # Get face embedding (resize to 160x160)
                            face_tensor = mtcnn(face_pil)
                            
                            if face_tensor is not None:
                                # Recognize face
                                name, distance = recognize_face(face_tensor, model, embeddings, device)
                                face_info = (name, distance, (x1, y1, x2, y2))
                                last_face_info = face_info
            except Exception as e:
                # Silently handle errors during processing
                pass
        
        # Use last detected face if current frame skipped processing
        if face_info is None and last_face_info is not None:
            face_info = last_face_info
        
        # Draw information on frame
        draw_info(frame, face_info, fps)
        
        # Display frame
        cv2.imshow("Face Recognition", frame)
        
        # Exit on ESC
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("\n🛑 Recognition stopped.")
    print("="*60)

if __name__ == "__main__":
    main()
