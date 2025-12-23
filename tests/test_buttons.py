#!/usr/bin/env python3
"""Test Button Inputs - 4 Buttons"""

import RPi.GPIO as GPIO
import time

# Button pins
BTN_LOCK = 17        # NEW!
BTN_PLAY = 23
BTN_VOL_UP = 24
BTN_VOL_DOWN = 25

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BTN_LOCK, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # NEW!
GPIO.setup(BTN_PLAY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_VOL_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_VOL_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Button Test - 4 Buttons")
print("\nPress buttons:")
print("  Button LOCK → State Lock")          # NEW!
print("  Button 1 → Volume Down")
print("  Button 2 → Volume Up")
print("  Button 3 → Play/Pause")
print("\nPress Ctrl+C to stop\n")

try:
    while True:
        if GPIO.input(BTN_LOCK) == GPIO.LOW:                  # NEW!
            print("Button LOCK pressed!")
            time.sleep(0.3)
        
        if GPIO.input(BTN_PLAY) == GPIO.LOW:
            print("Button 1 (Volume Down) pressed!")
            time.sleep(0.3)
        
        if GPIO.input(BTN_VOL_UP) == GPIO.LOW:
            print("Button 2 (Volume Up) pressed!")
            time.sleep(0.3)
        
        if GPIO.input(BTN_VOL_DOWN) == GPIO.LOW:
            print("Button 3 (Play/Pause) pressed!")
            time.sleep(0.3)
        
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n✓ Test complete")
finally:
    GPIO.cleanup()
