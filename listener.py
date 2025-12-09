import evdev
from evdev import ecodes
import threading
import sys
import os
import selectors

class MouseListener:
    def __init__(self, callback):
        self.callback = callback
        self.stop_event = threading.Event()
        self.thread = None

    def get_mouse_devices(self):
        mouse_devices = []
        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            for device in devices:
                # Check capabilities for BTN_RIGHT
                caps = device.capabilities()
                if ecodes.EV_KEY in caps:
                    if ecodes.BTN_RIGHT in caps[ecodes.EV_KEY]:
                        mouse_devices.append(device)
            return mouse_devices
        except OSError:
            return []

    def _run(self):
        devices = self.get_mouse_devices()
        if not devices:
            print("Error: No mouse devices found or permission denied!")
            print("Please run with 'sudo' or add your user to the 'input' group.")
            return

        print(f"Listening on {len(devices)} devices:")
        for dev in devices:
            print(f" - {dev.name} ({dev.path})")

        selector = selectors.DefaultSelector()
        for dev in devices:
            selector.register(dev, selectors.EVENT_READ)

        try:
            while not self.stop_event.is_set():
                for key, mask in selector.select(timeout=1):
                    if self.stop_event.is_set():
                        break
                    
                    device = key.fileobj
                    try:
                        for event in device.read():
                            if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_RIGHT and event.value == 1:
                                # 1 is pressed
                                threading.Thread(target=self.callback).start()
                    except OSError:
                        # Device might have been disconnected
                        selector.unregister(device)
                        print(f"Device {device.name} disconnected.")
                        
        except PermissionError:
            print(f"Error: Permission denied.")
            print("Please run with 'sudo'.")
            os._exit(1)
        except Exception as e:
            print(f"Error in listener: {e}")
        finally:
            selector.close()
            for dev in devices:
                dev.close()

    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.stop_event.set()
