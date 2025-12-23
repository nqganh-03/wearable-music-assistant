#!/usr/bin/env python3
"""
Wearable Music Assistant - Main Integration
Automatically plays music based on detected activity
"""

import sys
import time
import smbus2

# Import our modules
from activity_classifier import ActivityClassifier
from music_controller import MusicController
from button_controller import ButtonController
from display_manager import DisplayManager

# MPU6050 Configuration
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

bus = smbus2.SMBus(1)

def init_mpu6050():
    """Initialize MPU6050 sensor"""
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)
    time.sleep(0.1)
    print("✓ MPU6050 initialized")

def read_raw_data(addr):
    """Read 16-bit signed value from sensor"""
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

def read_accelerometer():
    """Read accelerometer values"""
    acc_x_raw = read_raw_data(ACCEL_XOUT_H)
    acc_y_raw = read_raw_data(ACCEL_XOUT_H + 2)
    acc_z_raw = read_raw_data(ACCEL_XOUT_H + 4)
    
    accel_x = acc_x_raw / 16384.0
    accel_y = acc_y_raw / 16384.0
    accel_z = acc_z_raw / 16384.0
    
    return accel_x, accel_y, accel_z

def main():
    print("=" * 70)
    print("WEARABLE MUSIC ASSISTANT")
    print("=" * 70)
    print("\nAutomatic music selection based on your activity")
    print("\nActivities:")
    print("  Staying still     → Calm tones (200 Hz)")
    print("  Light walking     → Moderate tones (600 Hz)")
    print("  Brisk walikng     → Energetic tones (800 Hz)")
    print("  Running/Intense   → Intense tones (1000 Hz)")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Initialize components
        print("Initializing...")
        init_mpu6050()
        classifier = ActivityClassifier()
        display = DisplayManager()
        music = MusicController(display)
        buttons = ButtonController(music, classifier, display)
        
        print("✓ Activity classifier ready")
        print("✓ Music controller ready")
        print("✓ Display manager ready")
        print("✓ Button controller ready")
        
        # Show startup message
        display.show_startup_message()
        
        print("✓ Starting initial music...")
        music.switch_playlist(0)
        print(f"→ Playing: {classifier.get_activity_name()}")
        
        # Initialize display state
        display.update_activity(classifier.get_activity_name())
        display.update_music_status(True)
        display.update_lock_status(False)
        
        print("\nSystem active! Move around to change music...\n")
        
        sample_count = 0
        
        while True:
            # Read sensor
            ax, ay, az = read_accelerometer()
            
            # Update classifier
            activity, changed, debug = classifier.update(ax, ay, az)
            
            # If activity changed, switch music
            if changed:
                music.switch_playlist(activity)
                activity_name = classifier.get_activity_name()
                print(f"→ Activity: {activity_name} (Variance: {debug['variance']:.4f})")
                
                # Update display
                display.update_activity(activity_name)
            
            # Display status (every 100 samples = 1 second)
            if sample_count % 100 == 0:
                activity_name = classifier.get_activity_name()
                lock_status = "🔒" if classifier.is_locked else "  "
                print(f"[{sample_count:05d}] {lock_status} {activity_name:12s} | Var: {debug['variance']:.4f} | Mag: {debug['mag']:.2f}g", end='\r')
            
            sample_count += 1
            time.sleep(0.01)  # 100Hz
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Stopping Wearable Music Assistant...")
        music.stop()
        music.cleanup()
        buttons.cleanup()
        display.cleanup()
        print("✓ Music stopped")
        print("✓ Buttons cleaned up")
        print("✓ Display cleaned up")
        print("✓ Sensor closed")
        print("=" * 70)
        print("\nGoodbye!\n")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        bus.close()

if __name__ == "__main__":
    main()
