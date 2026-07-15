import subprocess
import threading
import time
import apprise

# 1. LIVE SYSTEM SETUP CONFIGURATION
# Paste your verified Discord webhook URL between the quotes below:
DISCORD_WEBHOOK_URL = "YOUR_ACTUAL_DISCORD_WEBHOOK_HERE"

# Real track geometry mapping matching your verified layout
BOX_LOCATIONS = {
    "CG 48.0": "Pullman Defect Detector (6 Miles North of Camp)",
    "CG 66.2": "Hartford / Bangor Defect Detector (12.2 Miles South of Camp)"
}

print("🚀 TRWNS Live Rig: Booting Linux Notification Infrastructure...")
apobj = apprise.Apprise()

if "YOUR_ACTUAL" not in DISCORD_WEBHOOK_URL:
    apobj.add(DISCORD_WEBHOOK_URL.replace("https://", "discord://"))
    # Send an instant confirmation ping to your phone app to prove the laptop is online
    apobj.notify(
        body="🟢 **TRWNS LIVE IS ONLINE!** Your camper laptop is now actively scanning the airwaves for CSX trains.",
        title="🛰️ Radio Sentinel Status"
    )

# 2. CONTINUOUS NOOELEC SDR ANCHOR LOOP
def run_live_carrier_scanner():
    # Squelch (-l 15) forces the Nooelec stick to block background static hiss.
    # It pipes raw 16kHz analog FM audio blocks straight out of the 161.100 MHz CSX Road frequency.
    cmd = ["rtl_fm", "-f", "161.100M", "-M", "fm", "-s", "16k", "-g", "42", "-l", "15"]
    
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("❌ CRITICAL ERROR: 'rtl_fm' is missing. Run: sudo apt install rtl-sdr")
        return

    print("📡 Monitoring Airwaves: Awaiting CSX automated broadcasts...")
    signal_start_time = None
    
    while True:
        # Pull small binary audio frame blocks from the antenna stream
        chunk = proc.stdout.read(2000)
        
        if len(chunk) > 0:
            # Squelch broke open! An active radio transmission is hitting your camper antenna
            if signal_start_time is None: 
                signal_start_time = time.time()
        else:
            # Squelch closed back down. The radio transmission has ended
            if signal_start_time is not None:
                total_duration = time.time() - signal_start_time
                print(f"📡 Intercepted signal length: {total_duration:.1f} seconds")
                
                # UNBROKEN CARRIER LENGTH SECTOR VALIDATION:
                # Normal short radio talk or quick interference clicks drop off in 1 to 5 seconds.
                # Automated defect boxes keep the transmitter wide open for 15 to 45 seconds straight.
                if total_duration > 15.0:
                    print("🚂 TRAIN EVENT DETECTED: Firing Apprise instant dispatch packet...")
                    
                    # Formulate the payload message text
                    message_body = (
                        f"🚨 **TRAIN ACTIVE NEAR WARNER CAMP!** 🚨\n\n"
                        f"📡 **Antenna Signal:** Unbroken radio carrier wave confirmed via live scanner.\n"
                        f"⏱️ **Broadcast Length:** {total_duration:.1f} seconds\n"
                        f"📍 **Intercept Zone:** CSX Grand Rapids Subdivision Corridor\n\n"
                        f"A train has just keyed up the local detector frequency! Head outside to the deck, it will pass the campground crossing shortly. 🚂💨"
                    )
                    
                    # Push directly into Discord app network lines
                    if "YOUR_ACTUAL" not in DISCORD_WEBHOOK_URL:
                        apobj.notify(body=message_body, title="🚂 ACTIVE TRAIN SPOTTED")
                        
                # Clear clock timers to reset back to quiet monitoring state
                signal_start_time = None
                
        time.sleep(0.05)

if __name__ == '__main__':
    run_live_carrier_scanner()
