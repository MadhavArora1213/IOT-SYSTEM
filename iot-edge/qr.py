import qrcode
import uuid
from datetime import datetime, timedelta
import os
import sys

# Store QR sessions
qr_store = {}

def clear_screen():
    """Clear console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header(title):
    """Display formatted header"""
    print("\n" + "="*60)
    print(f"🤖 {title}")
    print("="*60)

def generate_strong_unique_id():
    """Generate highly unique 12-character QR ID"""
    return uuid.uuid4().hex[:12]

def format_qr_text(data):
    """Generate clean, line-by-line text for QR"""
    lines = []
    for key, value in data.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)

def generate_qr(details):
    """Generate QR code with given details"""
    display_header("GENERATING GATEPASS QR")
    
    # Generate unique ID
    qr_id = generate_strong_unique_id()
    
    # Set expiry time (15 minutes from now)
    expiry = datetime.now() + timedelta(minutes=15)
    expiry_str = expiry.strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare data for QR
    qr_data = {
        "GATEPASS SYSTEM": "SMART COLLEGE",
        "TYPE": details.get("type", "SINGLE"),
        "NAME": details.get("name", "").upper(),
        "ROLL NO": details.get("roll", ""),
        "CLASS": details.get("class", ""),
        "DESTINATION": details.get("destination", ""),
        "REASON": details.get("reason", ""),
        "OUT TIME": details.get("out_time", ""),
        "IN TIME": details.get("in_time", ""),
        "QR ID": qr_id,
        "GENERATED": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "VALID TILL": expiry_str,
        "STATUS": "ACTIVE"
    }
    
    # Generate QR text
    qr_text = format_qr_text(qr_data)
    
    # Create QR code with better settings
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_text)
    qr.make(fit=True)
    
    # Create and save QR image
    file_name = f"QR_{details.get('roll', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    # Create QR_images folder if it doesn't exist
    os.makedirs('QR_images', exist_ok=True)
    file_path = os.path.join('QR_images', file_name)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)
    
    # Store in session
    qr_store[details["roll"]] = {
        "qr_id": qr_id,
        "expires_at": expiry,
        "name": details["name"],
        "generated_at": datetime.now(),
        "file_path": file_path
    }
    
    # Display success message
    print("\n✅ QR CODE GENERATED SUCCESSFULLY!")
    print("="*60)
    
    # Display QR details
    print("\n📋 GATEPASS DETAILS:")
    print("-"*40)
    for key, value in qr_data.items():
        if key not in ["QR ID", "VALID TILL", "GENERATED"]:
            print(f"  {key:<15}: {value}")
    
    print("\n🔐 SECURITY INFO:")
    print("-"*40)
    print(f"  QR ID          : {qr_id}")
    print(f"  Generated      : {qr_data['GENERATED']}")
    print(f"  Valid Until    : {expiry_str}")
    print(f"  Time Remaining : 15 minutes")
    
    print(f"\n💾 QR CODE SAVED AS:")
    print(f"  {file_path}")
    
    print("\n📱 Scan this QR code at the gate for verification.")
    print("="*60)
    
    input("\nPress Enter to continue...")

def check_qr_status():
    """Check if a QR is expired or still valid"""
    display_header("CHECK QR STATUS")
    
    roll = input("Enter Roll Number: ").strip()
    
    if not roll:
        print("❌ Roll number cannot be empty!")
        return
    
    if roll not in qr_store:
        print(f"❌ No active QR found for roll number: {roll}")
        return
    
    qr_info = qr_store[roll]
    now = datetime.now()
    expiry = qr_info["expires_at"]
    
    print(f"\n👤 Student: {qr_info['name']}")
    print(f"🎫 QR ID: {qr_info['qr_id']}")
    print(f"📅 Generated: {qr_info['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Expires: {expiry.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if now > expiry:
        print("\n❌ STATUS: EXPIRED")
        print("   This QR code is no longer valid.")
    else:
        time_left = expiry - now
        minutes_left = int(time_left.total_seconds() / 60)
        seconds_left = int(time_left.total_seconds() % 60)
        
        print(f"\n✅ STATUS: ACTIVE")
        print(f"   Time remaining: {minutes_left} minutes {seconds_left} seconds")
        print(f"   QR File: {qr_info['file_path']}")
    
    input("\nPress Enter to continue...")

def view_all_qr_codes():
    """View all generated QR codes"""
    display_header("ALL GENERATED QR CODES")
    
    if not qr_store:
        print("No QR codes have been generated yet.")
        return
    
    print(f"Total QR Codes: {len(qr_store)}\n")
    print("-"*70)
    print(f"{'Roll No':<12} {'Name':<20} {'QR ID':<15} {'Status':<10} {'Expires In':<15}")
    print("-"*70)
    
    now = datetime.now()
    for roll, info in qr_store.items():
        status = "ACTIVE" if now <= info["expires_at"] else "EXPIRED"
        
        if status == "ACTIVE":
            time_left = info["expires_at"] - now
            expires_in = f"{int(time_left.total_seconds()/60)} min"
        else:
            expires_in = "EXPIRED"
        
        print(f"{roll:<12} {info['name'][:19]:<20} {info['qr_id']:<15} {status:<10} {expires_in:<15}")
    
    print("-"*70)
    input("\nPress Enter to continue...")

def delete_expired_qr():
    """Delete expired QR codes from memory"""
    display_header("CLEANUP EXPIRED QR CODES")
    
    now = datetime.now()
    expired_count = 0
    
    # Find expired QR codes
    expired_rolls = []
    for roll, info in qr_store.items():
        if now > info["expires_at"]:
            expired_rolls.append(roll)
    
    # Remove expired QR codes
    for roll in expired_rolls:
        del qr_store[roll]
        expired_count += 1
    
    if expired_count > 0:
        print(f"✅ Removed {expired_count} expired QR code(s) from memory.")
    else:
        print("ℹ️ No expired QR codes found.")
    
    print(f"📊 Active QR codes in memory: {len(qr_store)}")
    input("\nPress Enter to continue...")

def get_gatepass_details():
    """Get gate pass details from user"""
    details = {}
    
    print("\n📝 ENTER GATEPASS DETAILS")
    print("-"*40)
    
    details["type"] = input("Pass Type (Single/Multi/Emergency): ").strip() or "Single"
    details["name"] = input("Full Name: ").strip()
    
    if not details["name"]:
        print("❌ Name is required!")
        return None
    
    details["roll"] = input("Roll Number: ").strip()
    
    if not details["roll"]:
        print("❌ Roll number is required!")
        return None
    
    details["class"] = input("Class/Section: ").strip() or "N/A"
    details["destination"] = input("Destination: ").strip() or "Outside Campus"
    details["reason"] = input("Reason for leaving: ").strip() or "Personal"
    
    # Get times with validation
    while True:
        out_time = input("Outgoing Time (HH:MM 24-hour format): ").strip()
        if ":" in out_time and len(out_time.split(":")) == 2:
            details["out_time"] = out_time
            break
        else:
            print("❌ Please enter time in HH:MM format (e.g., 14:30)")
    
    while True:
        in_time = input("Expected Return Time (HH:MM): ").strip()
        if ":" in in_time and len(in_time.split(":")) == 2:
            details["in_time"] = in_time
            break
        else:
            print("❌ Please enter time in HH:MM format (e.g., 16:30)")
    
    return details

def main_menu():
    """Display main menu"""
    display_header("SMART GATEPASS SYSTEM")
    
    print("1. 📄 Generate New GatePass QR")
    print("2. 🔍 Check QR Status")
    print("3. 📋 View All QR Codes")
    print("4. 🗑️  Cleanup Expired QR Codes")
    print("5. 🚪 Exit")
    print("="*60)
    
    return input("\nEnter your choice (1-5): ").strip()

def main():
    """Main program loop"""
    while True:
        clear_screen()
        choice = main_menu()
        
        if choice == "1":
            clear_screen()
            details = get_gatepass_details()
            if details:
                generate_qr(details)
        
        elif choice == "2":
            clear_screen()
            check_qr_status()
        
        elif choice == "3":
            clear_screen()
            view_all_qr_codes()
        
        elif choice == "4":
            clear_screen()
            delete_expired_qr()
        
        elif choice == "5":
            clear_screen()
            display_header("EXITING SYSTEM")
            print("\n👋 Thank you for using Smart GatePass System!")
            print("="*60)
            break
        
        else:
            print("\n❌ Invalid choice! Please enter 1-5.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted. Exiting...")
        sys.exit(0)
