import os
import winreg
import hashlib
from datetime import datetime, timedelta
from core.hardware_id import get_machine_id

REG_PATH = r"Software\HoneypotAnalytics"
SECRET_SALT = "D@n10_!hNy_505#01_oLax_77$9" # Change this to your own private string!

def get_install_date():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        date_str, _ = winreg.QueryValueEx(key, "InstallDate")
        return datetime.strptime(date_str, "%Y-%m-%d")
    except FileNotFoundError:
        now = datetime.now().strftime("%Y-%m-%d")
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        winreg.SetValueEx(key, "InstallDate", 0, winreg.REG_SZ, now)
        return datetime.now()

def verify_license():
    install_date = get_install_date()
    
    # 30-day grace period check
    if datetime.now() <= install_date + timedelta(days=30):
        return True # Within trial period
    
    # After 30 days, verify license file
    if os.path.exists("license.key"):
        with open("license.key", "r") as f:
            saved_key = f.read().strip()
            
            # Re-generate the expected hash for this specific machine
            expected_key = hashlib.sha256((get_machine_id() + SECRET_SALT).encode()).hexdigest()
            
            return saved_key == expected_key
            
    return False # Trial expired and no valid key