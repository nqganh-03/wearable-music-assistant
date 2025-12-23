#!/usr/bin/env python3
"""
Test Activity Detection
Real-time activity classification from MPU6050
"""

import sys
sys.path.append('/home/pi/music-player/src')

import smbus2
import time
from activity_classifier import ActivityClassifier

# MPU6050 Configuration
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

bus = smbus2.SMBus(1)

def init_mpu6050():
    """Initialize sensor"""
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)
    time.sleep(0.1)

def read_raw_data(addr):
    """Read 16-bit signed value"""
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
    print("=" * 60)
    print("Real-Time Activity Detection")
    print("=" * 60)
    print("\nMove the sensor to test activity detection:")
    print("  - Keep still     → SITTING")
    print("  - Gentle motion  → WALKING")
    print("  - Vigorous shake → RUNNING")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Initialize
        init_mpu6050()
        classifier = ActivityClassifier()
        
        print("Reading sensor... (10-reading hysteresis active)\n")
        
        sample_count = 0
        
        while True:
            # Read sensor
            ax, ay, az = read_accelerometer()
            
            # Display current state
            activity, changed, debug = classifier.update(ax, ay, az)
            activity_name = classifier.get_activity_name()
            print(f"[{sample_count:04d}] Mag: {debug['mag']:4.2f}g  Var: {debug['variance']:6.4f}  |  {activity_name:10s}", end='')
            
            if changed:
                print("  ← CHANGED!", end='')
            
            print('\r', end='')
            
            sample_count += 1
            time.sleep(0.01)  # 100Hz
            
    except KeyboardInterrupt:
        print("\n\n✓ Test stopped")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        bus.close()
        print("✓ Sensor closed\n")

if __name__ == "__main__":
    main()
