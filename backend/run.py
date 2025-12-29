import uvicorn
import os
import sys

# Ensure the app directory is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

if __name__ == "__main__":
    # Point uvicorn to app.main:app
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
