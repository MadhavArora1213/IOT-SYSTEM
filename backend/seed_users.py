import sys
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import uuid
from PIL import Image, ImageDraw

# Add current directory to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize Firebase (Manual init to avoid potential circular imports or path issues)
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
users_ref = db.collection('users')

STORAGE_PATH = "Storage/Images"
os.makedirs(STORAGE_PATH, exist_ok=True)

def create_dummy_image(reg_no):
    image_filename = f"{reg_no}_{uuid.uuid4()}.jpg"
    file_path = os.path.join(STORAGE_PATH, image_filename)
    
    # Create a simple image
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10,10), reg_no, fill=(255, 255, 0))
    
    img.save(file_path)
    return file_path, image_filename

users_to_seed = [
    {
        "reg_no": "REG101",
        "password": "password123",
        "email": "user1@example.com",
        "phone": "1234567890",
        "class": "CS-A",
        "department": "Computer Science",
        "hod_name": "Dr. Smith",
        "incharge_name": "Mr. Doe",
        "valid_until": "2025-12-31"
    },
    {
        "reg_no": "REG102",
        "password": "password123",
        "email": "user2@example.com",
        "phone": "0987654321",
        "class": "CS-B",
        "department": "Computer Science",
        "hod_name": "Dr. Smith",
        "incharge_name": "Ms. Jane",
        "valid_until": "2025-12-31"
    },
    {
        "reg_no": "REG103",
        "password": "password123",
        "email": "user3@example.com",
        "phone": "1122334455",
        "class": "IT-A",
        "department": "Information Technology",
        "hod_name": "Dr. Brown",
        "incharge_name": "Mr. Green",
        "valid_until": "2025-12-31"
    }
]

def seed():
    print("Seeding users...")
    for user in users_to_seed:
        reg_no = user['reg_no']
        doc = users_ref.document(reg_no).get()
        if not doc.exists:
            print(f"Creating user {reg_no}...")
            file_path, filename = create_dummy_image(reg_no)
            
            user_data = user.copy()
            user_data['created_at'] = datetime.now().isoformat()
            user_data['image_path'] = file_path
            user_data['image_filename'] = filename
            
            users_ref.document(reg_no).set(user_data)
            print(f"User {reg_no} created.")
        else:
            print(f"User {reg_no} already exists.")

if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print(f"Error seeding: {e}")
        import traceback
        traceback.print_exc()
