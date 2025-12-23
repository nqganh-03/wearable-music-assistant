#!/bin/bash
# Wearable Music Assistant - Startup Script

# Wait for system to fully boot
sleep 10

# Set Galaxy Buds as default audio output
pactl set-default-sink bluez_output.44_EA_30_3B_BA_47.1

# Start MPD if not running
if ! pgrep -x "mpd" > /dev/null; then
    mpd ~/.config/mpd/mpd.conf
fi

# Wait for MPD to start
sleep 2

# Update MPD database
mpc update

# Enable repeat mode
mpc repeat on

# Activate virtual environment and start application
cd /home/pi/music-player
source venv/bin/activate
python3 src/main.py

# If program exits, log it
echo "Music Assistant stopped at $(date)" >> ~/music-player/stop.log
