#!/bin/bash
# Complete stop script

echo "Stopping Wearable Music Assistant..."

# Stop service
systemctl --user stop music-assistant.service

# Stop music playback
mpc stop

# Stop MPD
mpd --kill

echo "✓ Everything stopped!"
