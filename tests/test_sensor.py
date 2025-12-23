#!/usr/bin/env python3
"""
MPU6050 Basic Test - Read All 6 Values
Tests sensor connection and displays real-time data
"""

import smbus2
import time
import math

# MPU6050 Configuration
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# Initialize I2C bus
bus = smbus2.SMBus(1)

def init_mpu6050():
    """Wake up MPU6050 (starts in sleep mode)"""
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)
    time.sleep(0.1)
    print("✓ MPU6050 initialized")

def read_raw_data(addr):
    """Read 16-bit signed value from sensor"""
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    
    # Combine bytes
    value = (high << 8) | low
    
    # Convert to signed
    if value > 32768:
        value -= 65536
    
    return value

def read_all_sensors():
    """Read all 6 sensor values (accel + gyro)"""
    
    # Read raw accelerometer data
    acc_x_raw = read_raw_data(ACCEL_XOUT_H)
    acc_y_raw = read_raw_data(ACCEL_XOUT_H + 2)
    acc_z_raw = read_raw_data(ACCEL_XOUT_H + 4)
    
    # Read raw gyroscope data
    gyro_x_raw = read_raw_data(GYRO_XOUT_H)
    gyro_y_raw = read_raw_data(GYRO_XOUT_H + 2)
    gyro_z_raw = read_raw_data(GYRO_XOUT_H + 4)
    
    # Convert to real units
    # Accelerometer: ±2g range, 16384 LSB/g
    accel_x = acc_x_raw / 16384.0
    accel_y = acc_y_raw / 16384.0
    accel_z = acc_z_raw / 16384.0
    
    # Gyroscope: ±250°/s range, 131 LSB/(°/s)
    gyro_x = gyro_x_raw / 131.0
    gyro_y = gyro_y_raw / 131.0
    gyro_z = gyro_z_raw / 131.0
    
    # Calculate magnitude
    magnitude = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
    
    return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, magnitude

def main():
    print("=" * 70)
    print("MPU6050 Sensor Test - All 6 Values + Magnitude")
    print("=" * 70)
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Initialize sensor
        init_mpu6050()
        
        print("\nReading sensor data at 10Hz...\n")
        print("Accel (g)                    Gyro (°/s)                  Mag (g)")
        print("-" * 70)
        
        while True:
            # Read all sensors
            ax, ay, az, gx, gy, gz, mag = read_all_sensors()
            
            # Display formatted output
            print(f"X:{ax:6.2f} Y:{ay:6.2f} Z:{az:6.2f}  |  "
                  f"X:{gx:7.1f} Y:{gy:7.1f} Z:{gz:7.1f}  |  "
                  f"{mag:5.2f}g", end='\r')
            
            time.sleep(0.1)  # 10Hz update
            
    except KeyboardInterrupt:
        print("\n\n✓ Test stopped")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        bus.close()
        print("✓ I2C bus closed\n")

if __name__ == "__main__":
    main()
