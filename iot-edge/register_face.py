from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import numpy as np
import torch
import os
from pathlib import Path
import cv2

def display_welcome():
    print("\n" + "="*60)
    print("🤖 FACE REGISTRATION SYSTEM")
    print("="*60)
    print("This will:")
    print("1. Detect faces in images from 'faces/' folder")
    print("2. Extract facial features (128D embeddings)")
    print("3. Save embeddings to 'embeddings/' folder")
    print("="*60)

def check_dependencies():
    """Check if required modules are installed"""
    try:
        import facenet_pytorch
        import torch
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n📦 Install with: pip install facenet-pytorch torch torchvision")
        return False

def main():
    display_welcome()
    
    if not check_dependencies():
        return
    
    # Create necessary folders
    os.makedirs('embeddings', exist_ok=True)
    os.makedirs('faces', exist_ok=True)
    
    # Check if faces folder has images
    if not os.path.exists('faces') or len(os.listdir('faces')) == 0:
        print("\n❌ No images found in 'faces/' folder.")
        print("📁 Please run 'capture_face.py' first to capture face images.")
        input("\nPress Enter to exit...")
        return
    
    # Initialize device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n📊 Using device: {device}")
    if device.type == 'cpu':
        print("⚠️  CPU mode will be slower. Consider using GPU for better performance.")
    
    try:
        # Initialize models
        print("🔄 Loading face detection model (MTCNN)...")
        mtcnn = MTCNN(
            image_size=160,
            margin=20,
            min_face_size=40,
            thresholds=[0.6, 0.7, 0.7],
            factor=0.709,
            post_process=True,
            device=device
        )
        
        print("🔄 Loading face recognition model (FaceNet)...")
        model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
        
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        print("📦 Make sure facenet-pytorch is properly installed.")
        return
    
    # Get all image files
    faces_dir = Path('faces')
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    image_files = [f for f in faces_dir.glob('*') if f.suffix.lower() in supported_formats]
    
    print(f"\n📁 Found {len(image_files)} image(s) in 'faces/' folder")
    
    if not image_files:
        print("❌ No valid images found.")
        return
    
    print("\n🔄 Processing faces...")
    print("-" * 50)
    
    success_count = 0
    failed_count = 0
    failed_files = []
    
    for idx, img_path in enumerate(image_files, 1):
        try:
            print(f"[{idx}/{len(image_files)}] Processing: {img_path.name}...", end=" ")
            
            # Load and convert image
            img = Image.open(img_path).convert('RGB')
            
            # Detect and align face
            face = mtcnn(img)
            
            if face is None:
                print("❌ No face detected")
                failed_count += 1
                failed_files.append((img_path.name, "No face detected"))
            else:
                # Generate embedding
                with torch.no_grad():
                    embedding = model(face.unsqueeze(0).to(device)).detach().cpu().numpy()
                
                # Normalize embedding
                embedding = embedding / np.linalg.norm(embedding)
                
                # Save embedding
                name = img_path.stem
                output_path = f'embeddings/{name}_embedding.npy'
                np.save(output_path, embedding)
                print(f"✅ Registered as '{name}'")
                success_count += 1
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}...")
            failed_count += 1
            failed_files.append((img_path.name, str(e)))
    
    # Display summary
    print("\n" + "="*50)
    print("📊 REGISTRATION SUMMARY")
    print("="*50)
    print(f"✅ Successfully registered: {success_count} face(s)")
    print(f"❌ Failed: {failed_count} face(s)")
    
    if failed_files:
        print("\n⚠️  Failed files:")
        for file, reason in failed_files:
            print(f"   • {file}: {reason}")
    
    print(f"\n📁 Embeddings saved in: embeddings/")
    
    # List registered people
    if success_count > 0:
        embedding_files = [f for f in os.listdir('embeddings') if f.endswith('_embedding.npy')]
        print(f"\n👤 Registered people:")
        for emb_file in embedding_files:
            name = emb_file.replace('_embedding.npy', '')
            print(f"   • {name}")
    
    print("\n✅ Registration complete!")
    print("🎯 Now you can run 'recognize_face.py' for face recognition.")
    print("="*50)

if __name__ == "__main__":
    main()
