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
        
        self.mtcnn = MTCNN(
            image_size=160, margin=20, min_face_size=40,
            thresholds=[0.6, 0.7, 0.7], factor=0.709,
            post_process=True, device=self.device
        )
        self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        self.embeddings = {}
        self.load_known_faces()

    def load_known_faces(self):
        """Load all registered face embeddings from the known_faces directory"""
        # For now, we expect .npy files or we'll process .jpg files on the fly
        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith(".npy"):
                name = filename.replace("_embedding.npy", "")
                self.embeddings[name] = np.load(os.path.join(self.known_faces_dir, filename))
            elif filename.endswith((".jpg", ".png")):
                name = os.path.splitext(filename)[0]
                self.register_face(name, os.path.join(self.known_faces_dir, filename))

    def get_embedding(self, image_input):
        """Generate a 128D embedding from an image (PIL object or path or bytes)"""
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
        
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding

    def register_face(self, name, image_path):
        """Process an image and save its embedding"""
        embedding = self.get_embedding(image_path)
        if embedding is not None:
            output_path = os.path.join(self.known_faces_dir, f"{name}_embedding.npy")
            np.save(output_path, embedding)
            self.embeddings[name] = embedding
            return True
        return False

    def verify_embedding(self, target_face_bytes, known_embedding_list):
        """Verify face bytes against a specific known embedding"""
        target_embedding = self.get_embedding(target_face_bytes)
        if target_embedding is None:
            return False, "No face detected in submitted image"
            
        # Ensure known is numpy array
        if isinstance(known_embedding_list, list):
            known_embedding = np.array(known_embedding_list)
        else:
            known_embedding = known_embedding_list
            
        distance = cosine(target_embedding.flatten(), known_embedding.flatten())
        
        if distance < 0.6: # Threshold
            return True, distance
        else:
            return False, distance

    def verify_face(self, face_image_bytes, expected_name):
        """Verify if the face in face_image_bytes matches expected_name (from loaded files)"""
        # ... existing implementation or wrapper ...
        if expected_name not in self.embeddings:
             return False, "User not registered with a face (locally)"
        return self.verify_embedding(face_image_bytes, self.embeddings[expected_name])

face_service = FaceService()
