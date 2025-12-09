import sys
import threading
import time
from PyQt6.QtWidgets import QApplication
from ui import OverlayWindow, OverlayController
from listener import MouseListener
from screen import take_screenshot
from ai import transcribe_screenshot, get_answer

def workflow(controller):
    print("Right click detected! Starting workflow...")
    # controller.update_text_signal.emit("Processing...")
    
    # 1. Take Screenshot
    screenshot_path = take_screenshot()
    if not screenshot_path:
        print("Screenshot failed")
        return

    print(f"Screenshot taken: {screenshot_path}")
    # controller.update_text_signal.emit("Transcribing...")

    # 2. Transcribe
    transcription = transcribe_screenshot(screenshot_path)
    if transcription.startswith("Error"):
        print(transcription)
        return

    print(f"Transcription: {transcription[:50]}...")
    # controller.update_text_signal.emit("Solving...")

    # 3. Get Answer
    answer = get_answer(transcription)
    print(f"Answer: {answer}")
    
    # 4. Update UI
    controller.update_text_signal.emit(answer)

def main():
    # Create the controller for thread-safe UI updates
    controller = OverlayController()

    # Define the callback for the mouse listener
    def on_right_click():
        workflow(controller)

    # Start the mouse listener
    # Note: On Wayland, pynput might not work globally. 
    # If it fails, you might need to use 'evdev' or run this script with specific permissions.
    listener = MouseListener(on_right_click)
    listener.start()
    print("Listening for right clicks...")

    # Start the UI (must be on the main thread)
    app = QApplication(sys.argv)
    window = OverlayWindow(controller)
    # window.show() # Start hidden
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        listener.stop()

if __name__ == "__main__":
    main()
