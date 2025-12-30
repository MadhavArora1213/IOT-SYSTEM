from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from config.firebase_config import get_firestore_client, get_auth_client
from datetime import datetime
import os
import shutil
import uuid
from services.face_service import face_service

router = APIRouter()

STORAGE_PATH = "Storage/Images"
os.makedirs(STORAGE_PATH, exist_ok=True)

@router.post("/register")
async def register_user(
    reg_no: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    class_name: str = Form(...),
    department: str = Form(...),
    hod_name: str = Form(...),
    incharge_name: str = Form(...),
    valid_until: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Register a new user with all details and save image to local storage.
    Creates an account in Firebase Auth and stores details in Firestore.
    """
    db = get_firestore_client()
    auth = get_auth_client()
    users_ref = db.collection('users')
    
    # Check if user already exists in Firestore
    docs = users_ref.where('reg_no', '==', reg_no).stream()
    if any(docs):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this Registration Number already exists"
        )

    # Create user in Firebase Auth
    firebase_uid = None
    try:
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=reg_no
        )
        firebase_uid = user_record.uid
        print(f"Firebase Auth user created: {firebase_uid}")
    except Exception as e:
        # If email already exists or other auth error
        raise HTTPException(status_code=400, detail=f"Firebase Auth Error: {str(e)}")

    # Save image
    try:
        file_extension = image.filename.split(".")[-1]
        image_filename = f"{reg_no}_{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(STORAGE_PATH, image_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        print(f"Image saved to {file_path}")
    except Exception as e:
        # Clean up Auth user if image save fails? 
        # For simplicity, we might leave the auth user or try to delete it.
        if firebase_uid:
            try:
                auth.delete_user(firebase_uid)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")

    # ... (images save block)

    # Generate Face Embedding
    embedding_list = None
    try:
        embedding = face_service.get_embedding(file_path)
        if embedding is None:
             # Cleanup
            if os.path.exists(file_path):
                os.remove(file_path)
            if firebase_uid:
                try: auth.delete_user(firebase_uid) 
                except: pass
            raise HTTPException(status_code=400, detail="No face detected in the image. Please upload a clear photo.")
        
        embedding_list = embedding.flatten().tolist()
        print(f"Face embedding generated for {reg_no}")
    except HTTPException:
        raise
    except Exception as e:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
        if firebase_uid:
            try: auth.delete_user(firebase_uid) 
            except: pass
        raise HTTPException(status_code=500, detail=f"Face processing error: {str(e)}")

    user_data = {
        "uid": firebase_uid,
        "reg_no": reg_no,
        "password": password, 
        "email": email,
        "phone": phone,
        "class": class_name,
        "department": department,
        "hod_name": hod_name,
        "incharge_name": incharge_name,
        "valid_until": valid_until,
        "created_at": datetime.now().isoformat(),
        "image_path": file_path,
        "image_filename": image_filename,
        "face_embedding": embedding_list
    }

    try:
        # Use reg_no as document ID for easy lookup
        users_ref.document(reg_no).set(user_data)
        return {"status": "success", "message": "User registered successfully", "reg_no": reg_no, "uid": firebase_uid}
    except Exception as e:
        # Cleanup image and auth user if db fails
        if os.path.exists(file_path):
            os.remove(file_path)
        if firebase_uid:
            try:
                auth.delete_user(firebase_uid)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/login")
async def login_user(
    reg_no: str = Form(...),
    password: str = Form(...)
):
    """
    Login with Registration Number and Password.
    """
    db = get_firestore_client()
    doc_ref = db.collection('users').document(reg_no)
    doc = doc_ref.get()

    if not doc.exists:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Registration Number or Password"
        )
    
    user_data = doc.to_dict()
    
    # Simple password check (plaintext as per assumed flow, normally use bcrypt)
    if user_data.get('password') != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Registration Number or Password"
        )

    # Return success (and maybe user details if needed)
    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "reg_no": user_data.get("reg_no"),
            "name": user_data.get("email"), # Or add name if requested, using email as placeholder/name
            "email": user_data.get("email"),
            "department": user_data.get("department"),
            "class": user_data.get("class"),
            "image": f"/images/{user_data.get('image_filename')}" if user_data.get('image_filename') else None
        }
    }
