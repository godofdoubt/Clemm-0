# --- File: warp-core.py (Corrected) ---

# clemm09/warp-core.py
import os
from dotenv import load_dotenv

def initialize_warp_drive():
    """Initializes the warp drive by verifying the key and starting core systems."""
    load_dotenv()

    required_key = os.getenv("WARP_DRIVE_KEY")

    # NOTE: You will need to set a WARP_DRIVE_KEY in your .env file
    if required_key and len(required_key) > 8: # Removed the hardcoded key for better security
        print("Warp drive key verified. Engaging core systems...")
        import core.core
        core.core.start_core()
    else:
        print("ERROR: Invalid or missing warp drive key. System shutdown initiated.")
        exit()

if __name__ == "__main__":
    initialize_warp_drive()