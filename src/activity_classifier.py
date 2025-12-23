#!/usr/bin/env python3
"""
Activity Classifier - 4 States
Gravity Compensated with Variance Detection
Includes state lock functionality
"""

import math
from collections import deque
import numpy as np

class ActivityClassifier:
    """
    Activity classifier using acceleration variance
    (gravity-compensated)
    """
    
    # Activity states
    STATE_LOWACTIVITY = 0
    STATE_WALKING = 1
    STATE_FASTWALK = 2
    STATE_RUNNING = 3
    
    # Thresholds (variance of acceleration, not magnitude)
    THRESH_LIGHTWALK = 0.01    # Variance threshold for lightwalk
    THRESH_WALKING = 0.03      # Variance threshold for walking
    THRESH_FASTWALK = 0.15     # Variance threshold for fastwalk
    THRESH_RUNNING = 0.75      # Variance threshold for running
    
    # Hysteresis parameters
    BUFFER_SIZE = 70
    WINDOW_SIZE = 30
    
    def __init__(self):
        self.buffer = deque(maxlen=self.BUFFER_SIZE)
        
        # Store raw acceleration values (not magnitude!)
        self.accel_x_window = deque(maxlen=self.WINDOW_SIZE)
        self.accel_y_window = deque(maxlen=self.WINDOW_SIZE)
        self.accel_z_window = deque(maxlen=self.WINDOW_SIZE)
        
        self.current_activity = self.STATE_LOWACTIVITY
        
        # Lock functionality
        self.is_locked = False
        self.locked_activity = None
        
    def classify_instant(self, total_variance):
        """Classify based on total acceleration variance"""
        if total_variance > self.THRESH_RUNNING:
            return self.STATE_RUNNING
        elif total_variance > self.THRESH_FASTWALK:
            return self.STATE_FASTWALK
        elif total_variance > self.THRESH_WALKING:
            return self.STATE_WALKING
        elif total_variance > self.THRESH_LIGHTWALK:
            return self.STATE_LOWACTIVITY
        else:
            return self.STATE_LOWACTIVITY
    
    def update(self, accel_x, accel_y, accel_z):
        """
        Update classifier with new sensor reading
        Uses VARIANCE of acceleration (movement intensity)
        """
        
        # If locked, return locked activity without updating
        if self.is_locked:
            mag = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
            return self.locked_activity, False, {"variance": 0, "mag": mag}
        
        # Add raw values to windows
        self.accel_x_window.append(accel_x)
        self.accel_y_window.append(accel_y)
        self.accel_z_window.append(accel_z)
        
        # Need enough samples
        if len(self.accel_x_window) < self.WINDOW_SIZE:
            mag = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
            return self.current_activity, False, {"variance": 0, "mag": mag}
        
        # Calculate variance of each axis
        # Variance = how much values change (movement!)
        var_x = np.var(self.accel_x_window)
        var_y = np.var(self.accel_y_window)
        var_z = np.var(self.accel_z_window)
        
        # Total variance (movement intensity)
        total_variance = var_x + var_y + var_z
        
        # Classify
        instant_activity = self.classify_instant(total_variance)
        
        # Hysteresis
        self.buffer.append(instant_activity)
        
        if len(self.buffer) == self.BUFFER_SIZE:
            if all(a == instant_activity for a in self.buffer):
                if instant_activity != self.current_activity:
                    self.current_activity = instant_activity
                    mag = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
                    return self.current_activity, True, {"variance": total_variance, "mag": mag}
        
        mag = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
        return self.current_activity, False, {"variance": total_variance, "mag": mag}
    
    def get_activity_name(self, activity=None):
        """Get activity name"""
        if activity is None:
            activity = self.current_activity
            
        names = {
            self.STATE_LOWACTIVITY: "Staying still",
            self.STATE_WALKING: "Light walking",
            self.STATE_FASTWALK: "Brisk walking",
            self.STATE_RUNNING: "Running/Intense"
        }
        return names.get(activity, "UNKNOWN")
    
    def lock_state(self):
        """Lock current activity state"""
        self.is_locked = True
        self.locked_activity = self.current_activity
        print(f"\n🔒 STATE LOCKED: {self.get_activity_name()}")
    
    def unlock_state(self):
        """Unlock activity state"""
        self.is_locked = False
        self.locked_activity = None
        print(f"\n🔓 STATE UNLOCKED")
    
    def toggle_lock(self):
        """Toggle lock state"""
        if self.is_locked:
            self.unlock_state()
        else:
            self.lock_state()
        return self.is_locked


if __name__ == "__main__":
    print("✓ Classifier module loaded")
