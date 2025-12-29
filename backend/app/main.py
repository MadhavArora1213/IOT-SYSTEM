from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import verify

app = FastAPI(
    title="IoT Smart Gate Pass API",
    description="Backend API for Smart QR Gate Pass and Visitor Management System",
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
app.include_router(verify.router, prefix="/api", tags=["Verification"])

@app.get("/")
async def root():
    return {"message": "Smart Gate Pass API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
