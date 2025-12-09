import evdev
from evdev import ecodes

print("Scanning for input devices...")
try:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    if not devices:
        print("No devices found! Are you running with sudo?")
    
    for device in devices:
        print(f"Device: {device.name}")
        print(f"  Path: {device.path}")
        print(f"  Phys: {device.phys}")
        
        caps = device.capabilities()
        if ecodes.EV_KEY in caps:
            if ecodes.BTN_RIGHT in caps[ecodes.EV_KEY]:
                print("  -> HAS RIGHT CLICK BUTTON (Candidate)")
            else:
                print("  -> No right click button")
        else:
            print("  -> No keys/buttons")
        print("-" * 20)

except Exception as e:
    print(f"Error scanning devices: {e}")
    print("Try running with 'sudo'")
