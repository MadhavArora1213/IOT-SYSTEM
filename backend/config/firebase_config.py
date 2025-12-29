import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    return firebase_admin.get_app()

def get_firestore_client():
    """Get Firestore database client"""
    initialize_firebase()
    return firestore.client()

def get_auth_client():
    """Get Firebase Auth client"""
    initialize_firebase()
    return auth
