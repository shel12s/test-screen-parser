import subprocess
import os
import time
from datetime import datetime

def get_user_command_prefix():
    """
    Returns a prefix list to run a command as the sudo-invoking user,
    preserving necessary Wayland environment variables.
    """
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user and os.geteuid() == 0:
        uid = os.environ.get('SUDO_UID', '1000')
        
        # Try to guess or get environment variables
        wayland_display = os.environ.get('WAYLAND_DISPLAY', 'wayland-0')
        xdg_runtime_dir = os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{uid}')
        
        return [
            'sudo', '-u', sudo_user, 
            'env', 
            f'WAYLAND_DISPLAY={wayland_display}',
            f'XDG_RUNTIME_DIR={xdg_runtime_dir}'
        ]
    return []

def take_screenshot(filename="screenshot.png"):
    """
    Takes a screenshot using grim (Wayland) or spectacle (KDE).
    Returns the path to the screenshot if successful, None otherwise.
    """
    filepath = os.path.abspath(filename)
    prefix = get_user_command_prefix()
    
    # Try grim first (standard Wayland)
    try:
        cmd = prefix + ["grim", filepath]
        subprocess.run(cmd, check=True, capture_output=True)
        return filepath
    except subprocess.CalledProcessError as e:
        # Only print if it's not just "command not found" (which is FileNotFoundError usually, but subprocess might wrap it)
        # Actually, if grim is missing, it raises FileNotFoundError if shell=False.
        # If it runs but fails, it raises CalledProcessError.
        print(f"Grim failed: {e.stderr.decode().strip()}")
    except FileNotFoundError:
        pass

    # Try spectacle (KDE specific)
    try:
        # -b: background, -n: non-interactive, -o: output
        cmd = prefix + ["spectacle", "-b", "-n", "-o", filepath]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Wait for file to be created (Spectacle might be async)
        for _ in range(20): # Wait up to 2 seconds
            if os.path.exists(filepath):
                time.sleep(0.1) # Small buffer to ensure write completion
                return filepath
            time.sleep(0.1)
            
        print(f"Error: Screenshot file not found at {filepath} after execution.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Spectacle failed: {e.stderr.decode().strip()}")
        print("Error: Could not take screenshot. Please ensure 'grim' or 'spectacle' is installed.")
        return None
    except FileNotFoundError:
        print("Error: Could not find 'spectacle' or 'grim'.")
        return None
