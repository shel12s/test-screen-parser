#!/bin/bash
cd "$(dirname "$0")"

# Check if we are running on Wayland
if [ -z "$WAYLAND_DISPLAY" ]; then
    export WAYLAND_DISPLAY=wayland-0
fi

# Use pkexec to ask for password graphically and run the script as root
# We preserve environment variables needed for GUI and Wayland
pkexec env DISPLAY=$DISPLAY \
           XAUTHORITY=$XAUTHORITY \
           WAYLAND_DISPLAY=$WAYLAND_DISPLAY \
           XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR \
           SUDO_USER=$USER \
           "$(pwd)/.venv/bin/python" "$(pwd)/main.py"
