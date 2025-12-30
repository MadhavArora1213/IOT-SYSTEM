from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.firebase_config import initialize_firebase
from routes import devices, sensors, auth, verify, user_routes, gate_pass_routes

# Initialize Firebase on startup
initialize_firebase()

app = FastAPI(
    title="IoT System API",
    description="Backend API for IoT System with Firebase",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os

# Mount the storage directory to serve images
storage_path = os.path.join(os.getcwd(), "Storage", "Images")
os.makedirs(storage_path, exist_ok=True)
app.mount("/images", StaticFiles(directory=storage_path), name="images")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])
app.include_router(sensors.router, prefix="/api/sensors", tags=["Sensors"])
app.include_router(verify.router, prefix="/api/gatepass", tags=["GatePass"])
app.include_router(user_routes.router, prefix="/api/users", tags=["Users"])
app.include_router(gate_pass_routes.router, prefix="/api/gate-pass", tags=["Gate Pass"])

@app.get("/")
async def root():
    return {"message": "IoT System API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
