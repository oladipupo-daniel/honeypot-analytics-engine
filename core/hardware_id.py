import subprocess

def get_machine_id():
    # This command gets the motherboard serial number on Windows
    cmd = "wmic baseboard get serialnumber"
    try:
        output = subprocess.check_output(cmd, shell=True).decode()
        serial = output.split('\n')[1].strip()
        return serial
    except:
        return "UNKNOWN_HARDWARE"