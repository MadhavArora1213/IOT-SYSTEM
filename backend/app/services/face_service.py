import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import numpy as np
import os
import io
from scipy.spatial.distance import cosine

class FaceService:
    def __init__(self, known_faces_dir="known_faces"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.known_faces_dir = known_faces_dir
        os.makedirs(self.known_faces_dir, exist_ok=True)
        
        # Initialize MTCNN for face detection
        self.mtcnn = MTCNN(
            image_size=160, margin=20, min_face_size=40,
            thresholds=[0.6, 0.7, 0.7], factor=0.709,
            post_process=True, device=self.device
        )
        
        # Initialize InceptionResnetV1 for face recognition
        self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        self.embeddings = {}
        self.load_known_faces()

    def load_known_faces(self):
        """Load registered face embeddings from the known_faces directory (recursive)"""
        if not os.path.exists(self.known_faces_dir):
            return
            
        for root, dirs, files in os.walk(self.known_faces_dir):
            for filename in files:
                if filename.endswith(".npy"):
                    name = filename.replace("_embedding.npy", "")
                    self.embeddings[name] = np.load(os.path.join(root, filename))
                elif filename.endswith((".jpg", ".png")):
                    # Use directory name as user roll/id if it's a subfolder
                    parent_dir = os.path.basename(root)
                    if parent_dir != os.path.basename(self.known_faces_dir):
                        name = parent_dir
                    else:
                        name = os.path.splitext(filename)[0]
                    
                    if name not in self.embeddings:
                        # Pass name so register_face creates subfolder
                        self.register_face(name, os.path.join(root, filename))

    def get_embedding(self, image_input):
        """Generate a 128D embedding from an image"""
        try:
            if isinstance(image_input, (str, bytes)):
                if isinstance(image_input, bytes):
                    img = Image.open(io.BytesIO(image_input)).convert('RGB')
                else:
                    img = Image.open(image_input).convert('RGB')
            else:
                img = image_input.convert('RGB')
                
            face = self.mtcnn(img)
            if face is None:
                return None
            
            with torch.no_grad():
                embedding = self.model(face.unsqueeze(0).to(self.device)).detach().cpu().numpy()
            
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def register_face(self, name, image_path):
        """Process an image and save its embedding for future verification"""
        embedding = self.get_embedding(image_path)
        if embedding is not None:
            user_dir = os.path.join(self.known_faces_dir, name)
            os.makedirs(user_dir, exist_ok=True)
            output_path = os.path.join(user_dir, "embedding.npy")
            np.save(output_path, embedding)
            self.embeddings[name] = embedding
            return True
        return False

    def save_registration_face(self, name, image_bytes):
        """Save a registration photo and its embedding during gatepass request"""
        user_dir = os.path.join(self.known_faces_dir, name)
        os.makedirs(user_dir, exist_ok=True)
        
        # Save raw image
        img_path = os.path.join(user_dir, "registration.jpg")
        with open(img_path, "wb") as f:
            f.write(image_bytes)
            
        # Generate and save embedding
        return self.register_face(name, img_path)

    def verify_face(self, face_image_bytes, expected_name):
        """Verify if the provided face matches the expected name"""
        if expected_name not in self.embeddings:
            # Fallback: check if the user directory exists
            user_dir = os.path.join(self.known_faces_dir, expected_name)
            if os.path.exists(user_dir):
                self.load_known_faces() # Re-scan
            
            if expected_name not in self.embeddings:
                return False, f"User '{expected_name}' not registered"
        
        target_embedding = self.get_embedding(face_image_bytes)
        if target_embedding is None:
            return False, "No face detected in capture"
        
        known_embedding = self.embeddings[expected_name]
        distance = cosine(target_embedding.flatten(), known_embedding.flatten())
        
        # Distance < 0.6 is a match (standard for FaceNet)
        if distance < 0.6:
            return True, distance
        else:
            return False, distance

face_service = FaceService()
