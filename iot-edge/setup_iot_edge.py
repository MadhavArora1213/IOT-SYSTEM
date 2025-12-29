import subprocess
import sys
import os

def run_command(command):
    """Run shell command and return success status"""
    try:
        print(f"📦 Running: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("="*60)
    print("🔧 SMART GATEPASS SYSTEM - SETUP & INSTALLER")
    print("="*60)
    
    # List of required packages
    packages = [
        "opencv-python",
        "keyboard",
        "facenet-pytorch",
        "torch",
        "torchvision",
        "pillow",
        "numpy",
        "scipy",
        "qrcode",
        "uuid",
        "pyzbar",
        "requests",
        "pyttsx3"
    ]
    
    print(f"\n📦 Will install/verify {len(packages)} packages:")
    for pkg in packages:
        print(f"   • {pkg}")
    
    # Check if we are in a venv
    is_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not is_venv:
        print("\n⚠️  WARNING: You are not in a virtual environment.")
        print("   It is highly recommended to use a venv.")
    
    input("\nPress Enter to start installation (or Ctrl+C to cancel)...")
    
    # Install packages
    success_count = 0
    fail_count = 0
    
    for pkg in packages:
        print(f"\n{'='*40}")
        print(f"Installing {pkg}...")
        
        if run_command(f"{sys.executable} -m pip install {pkg}"):
            print(f"✅ {pkg} installed successfully")
            success_count += 1
        else:
            print(f"❌ Failed to install {pkg}")
            fail_count += 1
    
    # Create necessary folders
    print(f"\n{'='*40}")
    print("📁 Creating/Verifying necessary folders...")
    
    folders = ['faces', 'embeddings', 'QR_images']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Verified: {folder}/")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SETUP SUMMARY:")
    print(f"{'='*60}")
    print(f"✅ Successfully installed: {success_count} packages")
    print(f"❌ Failed: {fail_count} packages")
    print(f"📁 Verified: {len(folders)} folders")
    
    if fail_count == 0:
        print(f"\n🎉 SYSTEM READY!")
        print("\n📋 NEXT STEPS (In separate terminals):")
        print("1. [BACKEND] Run 'python run.py' from the backend folder")
        print("2. [SETUP]   Run 'python capture_face.py' to capture your face")
        print("3. [SETUP]   Run 'python register_face.py' to process embeddings")
        print("4. [SETUP]   Run 'python qr.py' to generate your gatepass")
        print("5. [RUN]     Run 'python main.py' to start the terminal emulator")
    else:
        print(f"\n⚠️  Some packages failed to install. Please check your internet or permissions.")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    main()
