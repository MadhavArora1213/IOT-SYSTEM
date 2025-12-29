from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.firebase_config import initialize_firebase
from routes import devices, sensors, auth

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

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])
app.include_router(sensors.router, prefix="/api/sensors", tags=["Sensors"])

@app.get("/")
async def root():
    return {"message": "IoT System API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
