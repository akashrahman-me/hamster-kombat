import os
import subprocess
import tempfile

def get_screenshot(device_id):
    temp_dir = tempfile.mkdtemp()
    screenshot_path = os.path.join(temp_dir, 'screenshot.png')

    # Modify the adb command to include the device ID
    adb_command = f"adb -s {device_id} exec-out screencap -p > {screenshot_path}"

    # Run the command using subprocess
    subprocess.run(adb_command, shell=True)

    # Check if the screenshot was successfully captured
    if not os.path.exists(screenshot_path):
        print("Failed to capture a screenshot.")
        return None

    return screenshot_path
