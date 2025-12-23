#!/usr/bin/env python3
"""
Test OLED Display
Verify SSD1306 is working
"""

import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
import time

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize display (128x64 pixels)
display = SSD1306_I2C(128, 64, i2c, addr=0x3c)

# Clear display
display.fill(0)
display.show()

print("OLED Display Test")
print("=" * 50)

# Create blank image
image = Image.new("1", (display.width, display.height))
draw = ImageDraw.Draw(image)

# Test 1: Text display
print("Test 1: Displaying text...")
draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0)
draw.text((0, 0), "Hello Pi!", fill=255)
draw.text((0, 16), "OLED Works!", fill=255)
draw.text((0, 32), "Music Player", fill=255)
draw.text((0, 48), "Ready!", fill=255)

display.image(image)
display.show()

time.sleep(3)

# Test 2: Animation
print("Test 2: Animation...")
for i in range(128):
    draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0)
    draw.rectangle((i, 20, i+10, 40), outline=255, fill=255)
    draw.text((30, 25), f"Progress", fill=255)
    display.image(image)
    display.show()
    time.sleep(0.02)

# Test 3: Different sizes
print("Test 3: Large text...")
draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0)
draw.text((10, 10), "BIG", fill=255)
draw.text((10, 40), "SUCCESS!", fill=255)

display.image(image)
display.show()

time.sleep(2)

# Clear
display.fill(0)
display.show()

print("\n✓ OLED test complete!")

