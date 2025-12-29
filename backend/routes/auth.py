from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from config.firebase_config import get_auth_client

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None

class TokenVerify(BaseModel):
    id_token: str

@router.post("/verify-token")
async def verify_token(token_data: TokenVerify):
    """Verify Firebase ID token"""
    try:
        auth = get_auth_client()
        decoded_token = auth.verify_id_token(token_data.id_token)
        return {"uid": decoded_token["uid"], "email": decoded_token.get("email")}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/create-user")
async def create_user(user: UserCreate):
    """Create a new user in Firebase Auth"""
    try:
        auth = get_auth_client()
        user_record = auth.create_user(
            email=user.email,
            password=user.password,
            display_name=user.display_name
        )
        return {"uid": user_record.uid, "email": user_record.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
