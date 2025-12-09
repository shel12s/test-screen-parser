from pynput import mouse

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Mouse clicked at ({x}, {y}) with {button}")

print("Testing mouse input. Please click anywhere. Press Ctrl+C to exit.")
# Collect events until released
with mouse.Listener(on_click=on_click) as listener:
    listener.join()
