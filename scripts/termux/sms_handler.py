#!/usr/bin/env python3
"""
KisanMitra SMS Bot - Termux Handler (Telugu)
Monitors SMS and responds to CROP-city, SUB, SCH commands.

Usage:
    python sms_handler.py

Commands:
    CROP-గుంటూరు  - పంట సిఫార్సులు (4 SMS)
    SUB           - సబ్సిడీల జాబితా (2 SMS)
    SCH           - పథకాల జాబితా (2 SMS)
    SUB-1         - సబ్సిడీ వివరాలు
    SCH-1         - పథకం వివరాలు
"""

import subprocess
import json
import time
import requests
import sys

# ============ CONFIGURATION ============
# Backend API URL - Use your PC's local IP address
# Find your IP: Windows -> ipconfig | Mac/Linux -> ifconfig
BACKEND_URL = "http://192.168.1.100:8001"  # <-- UPDATE THIS WITH YOUR PC IP

BOT_PHONE = "+917330671778"  # Your phone number (optional logging)
CHECK_INTERVAL = 5  # seconds between SMS checks
SMS_DELAY = 1  # seconds between multi-part SMS sends
LAST_SMS_ID = None
# =======================================


def run_termux_command(command):
    """Run a Termux API command and return output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Termux error: {e}")
        return None


def get_latest_sms():
    """Get the latest SMS messages."""
    output = run_termux_command(["termux-sms-list", "-l", "5"])
    if output:
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            print("Error parsing SMS list")
    return []


def send_sms(phone_number, message):
    """Send an SMS reply."""
    # Truncate if too long
    if len(message) > 1000:
        message = message[:997] + "..."
    
    result = run_termux_command([
        "termux-sms-send",
        "-n", phone_number,
        message
    ])
    return result is not None


def send_multi_sms(phone_number, messages):
    """Send multiple SMS parts with delay between each."""
    for i, msg in enumerate(messages):
        print(f"   📤 Sending part {i+1}/{len(messages)}...")
        if send_sms(phone_number, msg):
            print(f"   ✅ Part {i+1} sent")
        else:
            print(f"   ❌ Part {i+1} failed")
        
        # Delay between messages (except last one)
        if i < len(messages) - 1:
            time.sleep(SMS_DELAY)


def call_backend(message, sender):
    """Call the backend API to process the SMS command."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/sms-webhook",
            json={
                "message": message,
                "sender": sender
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            should_respond = data.get("should_respond", False)
            responses = data.get("responses", [])
            
            # Fallback to single response for backward compatibility
            if not responses and data.get("response"):
                responses = [data.get("response")]
            
            return (should_respond, responses)
        else:
            print(f"   ⚠️ Backend returned {response.status_code}")
            return (False, [])
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to {BACKEND_URL}")
        return (False, [])
    except Exception as e:
        print(f"   ❌ Backend error: {e}")
        return (False, [])


def process_sms(sms):
    """Process an incoming SMS and send response."""
    sender = sms.get("number", "")
    body = sms.get("body", "").strip()
    sms_id = sms.get("_id")
    
    print(f"\n📨 New SMS from {sender}")
    print(f"   Message: {body}")
    
    # Get responses from backend
    should_respond, responses = call_backend(body, sender)
    
    if should_respond and responses:
        print(f"   📋 Got {len(responses)} SMS parts")
        send_multi_sms(sender, responses)
    else:
        print(f"   ⏭️ Ignored (not a valid command)")
    
    return sms_id


def main():
    """Main loop to monitor SMS."""
    global LAST_SMS_ID
    
    print("=" * 50)
    print("🌾 KisanMitra SMS Bot (Telugu)")
    print("=" * 50)
    print(f"Backend: {BACKEND_URL}")
    print(f"Check interval: {CHECK_INTERVAL}s")
    print("\nకమాండ్లు:")
    print("  CROP-గుంటూరు  → పంట సిఫార్సులు")
    print("  SUB           → సబ్సిడీల జాబితా")
    print("  SCH           → పథకాల జాబితా")
    print("  SUB-1         → సబ్సిడీ వివరాలు")
    print("  SCH-1         → పథకం వివరాలు")
    print("\nPress Ctrl+C to stop\n")
    
    # Test backend connection
    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=5)
        if r.status_code == 200:
            print("✅ Backend connected\n")
        else:
            print(f"⚠️ Backend returned {r.status_code}\n")
    except:
        print(f"❌ Cannot connect to {BACKEND_URL}")
        print("   Check your PC IP and ensure backend is running\n")
    
    # Get initial SMS ID to avoid processing old messages
    messages = get_latest_sms()
    if messages:
        LAST_SMS_ID = messages[0].get("_id")
        print(f"Starting from SMS ID: {LAST_SMS_ID}\n")
    
    while True:
        try:
            messages = get_latest_sms()
            
            for sms in messages:
                sms_id = sms.get("_id")
                sms_type = sms.get("type", "")
                
                # Only process new incoming messages
                if sms_type == "inbox" and (LAST_SMS_ID is None or sms_id > LAST_SMS_ID):
                    LAST_SMS_ID = process_sms(sms)
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 SMS Bot stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(CHECK_INTERVAL)


def test_mode():
    """Test mode for PC without Termux."""
    print("\n🧪 TEST MODE - Simulating SMS")
    print(f"Backend: {BACKEND_URL}\n")
    
    # Test connection
    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=5)
        print(f"✅ Backend connected\n")
    except:
        print(f"❌ Cannot connect to {BACKEND_URL}\n")
        return
    
    while True:
        msg = input("\nEnter SMS command (or 'quit'): ").strip()
        if msg.lower() == 'quit':
            break
        
        should_respond, responses = call_backend(msg, "TEST")
        
        if should_respond and responses:
            print(f"\n📱 Would send {len(responses)} SMS:")
            for i, resp in enumerate(responses):
                print(f"\n--- SMS {i+1}/{len(responses)} ---")
                print(resp)
        else:
            print("\n⏭️ Not a valid command")


if __name__ == "__main__":
    # Check if running in Termux
    try:
        subprocess.run(["termux-sms-list", "-l", "1"], capture_output=True, timeout=5)
        main()
    except FileNotFoundError:
        print("⚠️ Termux API not found!")
        print("\nTo install on Android:")
        print("1. Install Termux from F-Droid")
        print("2. Install Termux:API from F-Droid")
        print("3. Run: pkg install termux-api")
        
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            test_mode()
        else:
            print("\nFor PC testing, run: python sms_handler.py --test")
        sys.exit(1)
