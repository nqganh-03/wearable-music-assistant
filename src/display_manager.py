#!/usr/bin/env python3
"""
Display Manager
Manages OLED display updates for status information
"""

import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
from threading import Thread, Lock
import time

class DisplayManager:
    """
    Manages OLED display with status information
    """
    
    def __init__(self):
        """Initialize OLED display"""
        # Initialize I2C
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Initialize display (128x64)
        self.display = SSD1306_I2C(128, 64, i2c, addr=0x3c)
        
        # Create blank image for drawing
        self.image = Image.new("1", (self.display.width, self.display.height))
        self.draw = ImageDraw.Draw(self.image)
        
        # Display state
        self.activity = "Staying still"
        self.song_name = "calm.wav"
        self.music_status = "Playing"
        self.is_locked = False
        self.volume = 50
        
        # Scrolling text state
        self.scroll_position = 0
        self.scroll_delay_counter = 0
        self.SCROLL_DELAY = 3  # Wait 3 frames before scrolling
        self.MAX_SONG_CHARS = 15  # Max chars that fit on screen
        
        # Thread control
        self.running = True
        self.lock = Lock()
        
        # Start update thread
        self.thread = Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        
        # Clear display
        self.display.fill(0)
        self.display.show()
        
        print("✓ Display manager ready")
    
    def update_activity(self, activity_name):
        """Update current activity"""
        with self.lock:
            self.activity = activity_name
    
    def update_song(self, song_name):
        """Update current song name"""
        with self.lock:
            # Extract just filename without path
            if '/' in song_name:
                song_name = song_name.split('/')[-1]
            
            # Reset scroll if song changed
            if song_name != self.song_name:
                self.scroll_position = 0
                self.scroll_delay_counter = 0
            
            self.song_name = song_name
    
    def update_music_status(self, is_playing):
        """Update music playback status"""
        with self.lock:
            self.music_status = "Playing" if is_playing else "Paused"
    
    def update_lock_status(self, is_locked):
        """Update state lock status"""
        with self.lock:
            self.is_locked = is_locked
    
    def update_volume(self, volume):
        """Update volume level"""
        with self.lock:
            self.volume = volume
    
    def _get_scrolling_text(self, text, max_chars):
        """
        Get scrolling text based on current scroll position
        
        Args:
            text: Full text to scroll
            max_chars: Maximum characters to display
        
        Returns:
            Substring to display
        """
        if len(text) <= max_chars:
            # Text fits, no scrolling needed
            return text
        
        # Add spacing for smooth loop
        full_text = text + "   "  # 3 spaces between loops
        
        # Increment scroll position
        if self.scroll_delay_counter < self.SCROLL_DELAY:
            # Wait before starting scroll
            self.scroll_delay_counter += 1
            return text[:max_chars]
        
        # Calculate what to show
        display_text = full_text[self.scroll_position:self.scroll_position + max_chars]
        
        # If we're near the end, wrap around
        if len(display_text) < max_chars:
            display_text += full_text[:max_chars - len(display_text)]
        
        # Advance scroll position
        self.scroll_position += 1
        if self.scroll_position >= len(full_text):
            self.scroll_position = 0
            self.scroll_delay_counter = 0  # Reset delay for next loop
        
        return display_text
    
    def _update_loop(self):
        """Background thread to update display"""
        while self.running:
            with self.lock:
                self._render_display()
            time.sleep(0.2)  # Update 5 times per second (smoother scrolling)
    
    def _render_display(self):
        """Render current status to display"""
        # Clear canvas
        self.draw.rectangle((0, 0, self.display.width, self.display.height), 
                          outline=0, fill=0)
        
        # Line 1: Title
        self.draw.text((0, 0), "MUSIC ASSISTANT", fill=255)
        
        # Line 2: Horizontal line
        self.draw.line((0, 12, 128, 12), fill=255)
        
        # Line 3: Activity (single line)
        activity_short = self.activity[:12]  # Limit length
        self.draw.text((0, 16), f"Act: {activity_short}", fill=255)
        
        # Line 4: Song name (scrolling if too long)
        song_display = self._get_scrolling_text(self.song_name, self.MAX_SONG_CHARS)
        self.draw.text((0, 28), f"Song: {song_display}", fill=255)
        
        # Line 5: Status icons
        y_pos = 42
        
        # Music status
        icon = ">" if self.music_status == "Playing" else "||"
        self.draw.text((0, y_pos), f"{icon} {self.music_status}", fill=255)
        
        # Lock status
        if self.is_locked:
            self.draw.text((90, y_pos), "LOCK", fill=255)
        
        # Line 6: Volume bar (bottom)
        bar_width = int((self.volume / 100) * 118)
        self.draw.rectangle((5, 56, 5 + bar_width, 60), outline=255, fill=255)
        self.draw.rectangle((5, 56, 123, 60), outline=255, fill=0)
        
        # Update display
        self.display.image(self.image)
        self.display.show()
    
    def show_startup_message(self):
        """Show startup message"""
        self.draw.rectangle((0, 0, self.display.width, self.display.height), 
                          outline=0, fill=0)
        self.draw.text((20, 10), "WEARABLE", fill=255)
        self.draw.text((25, 25), "MUSIC", fill=255)
        self.draw.text((15, 40), "ASSISTANT", fill=255)
        self.display.image(self.image)
        self.display.show()
        time.sleep(2)
    
    def cleanup(self):
        """Stop display updates and clear screen"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1)
        self.display.fill(0)
        self.display.show()
        print("✓ Display cleaned up")


if __name__ == "__main__":
    # Test display manager
    print("Testing Display Manager...")
    
    display = DisplayManager()
    display.show_startup_message()
    
    # Test different states with scrolling
    test_songs = [
        "Short.mp3",
        "Medium-Length-Song.mp3",
        "Very-Long-Song-Name-That-Will-Scroll.mp3"
    ]
    
    states = ["Staying still", "Light walking", "Brisk walking", "Running/Intense"]
    
    for i, state in enumerate(states):
        display.update_activity(state)
        display.update_song(test_songs[i % len(test_songs)])
        display.update_volume(25 * (i + 1))
        display.update_music_status(i % 2 == 0)
        display.update_lock_status(i == 2)
        time.sleep(5)  # Watch scrolling
    
    display.cleanup()
    print("✓ Display test complete!")
