#!/usr/bin/env python3
"""
Button Controller
Handles physical button inputs with debouncing
"""

import RPi.GPIO as GPIO
import time
from threading import Thread

class ButtonController:
    """
    Manages physical button inputs
    """
    
    # GPIO pins (adjusted based on your preference)
    BTN_LOCK = 17        # Button 4: State Lock
    BTN_VOL_DOWN = 23    # Button 1: Volume Down
    BTN_VOL_UP = 24      # Button 2: Volume Up
    BTN_PLAY = 25        # Button 3: Play/Pause
    
    # Debounce time (seconds)
    DEBOUNCE_TIME = 0.2
    
    def __init__(self, music_controller, activity_classifier, display_manager):
        """
        Initialize button controller
        
        Args:
            music_controller: MusicController instance
            activity_classifier: ActivityClassifier instance
            display_manager: DisplayManager instance
        """
        self.music = music_controller
        self.classifier = activity_classifier
        self.display = display_manager
        
        # Last press times (for debouncing)
        self.last_press = {
            self.BTN_LOCK: 0,
            self.BTN_PLAY: 0,
            self.BTN_VOL_UP: 0,
            self.BTN_VOL_DOWN: 0
        }
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BTN_LOCK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BTN_PLAY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BTN_VOL_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BTN_VOL_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Start monitoring thread
        self.running = True
        self.thread = Thread(target=self._monitor_buttons, daemon=True)
        self.thread.start()
        
        print("✓ Button controller ready")
    
    def _debounce(self, pin):
        """Check if enough time has passed since last press"""
        now = time.time()
        if now - self.last_press[pin] > self.DEBOUNCE_TIME:
            self.last_press[pin] = now
            return True
        return False
    
    def _monitor_buttons(self):
        """Monitor button presses in background thread"""
        while self.running:
            # Lock button
            if GPIO.input(self.BTN_LOCK) == GPIO.LOW:
                if self._debounce(self.BTN_LOCK):
                    is_locked = self.classifier.toggle_lock()
                    self.display.update_lock_status(is_locked)
                    status = "LOCKED" if is_locked else "UNLOCKED"
                    print(f"\n🔒 State {status}")
            
            # Play/Pause button
            if GPIO.input(self.BTN_PLAY) == GPIO.LOW:
                if self._debounce(self.BTN_PLAY):
                    if self.music.is_playing:
                        self.music.pause()
                        self.display.update_music_status(False)
                    else:
                        self.music.play()
                        self.display.update_music_status(True)
            
            # Volume Up button
            if GPIO.input(self.BTN_VOL_UP) == GPIO.LOW:
                if self._debounce(self.BTN_VOL_UP):
                    self.music.volume_up()
            
            # Volume Down button
            if GPIO.input(self.BTN_VOL_DOWN) == GPIO.LOW:
                if self._debounce(self.BTN_VOL_DOWN):
                    self.music.volume_down()
            
            time.sleep(0.01)  # 100Hz polling
    
    def cleanup(self):
        """Stop monitoring and cleanup GPIO"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1)
        GPIO.cleanup()
        print("✓ Buttons cleaned up")


if __name__ == "__main__":
    print("✓ Button controller module loaded")
