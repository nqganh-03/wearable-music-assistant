# Wearable Music Assistant

A wearable music assistant device using Raspberry Pi Zero 2 W that automatically selects and plays music based on detected physical activity. The system uses motion sensor data to classify user activities and switches music playlists accordingly.

## Features

- **Real-time Activity Detection**: Classifies physical activity (staying still, light walking, brisk walking, running)
- **Automatic Playlist Switching**: Changes music based on detected activity
- **Bluetooth Audio**: Wireless audio output to Bluetooth earbuds
- **Physical Controls**: 4 buttons for state lock, play/pause, and volume control
- **OLED Display**: Shows current activity, song name, and playback status with scrolling text
- **Auto-start on Boot**: Fully autonomous operation
- **Manual Override**: Lock playlist or pause without auto-resume

## Hardware Requirements

### Components
- Raspberry Pi Zero 2 W (512MB RAM)
- MPU6050 6-axis motion sensor (I2C)
- SSD1306 OLED display 128x64 (I2C)
- 4 tactile push buttons (GPIO)
- Bluetooth earbuds (e.g., Galaxy Buds Pro)
- Breadboard and jumper wires
- Power supply/battery

### Pin Connections

| Component | Pin # | GPIO # | Function |
|-----------|-------|--------|----------|
| **MPU6050** |
| VCC | 1 | - | 3.3V Power |
| SDA | 3 | GPIO 2 | I2C Data |
| SCL | 5 | GPIO 3 | I2C Clock |
| GND | 6 | - | Ground |
| **OLED Display** |
| VCC | 1 | - | 3.3V Power |
| SDA | 3 | GPIO 2 | I2C Data |
| SCL | 5 | GPIO 3 | I2C Clock |
| GND | 6 | - | Ground |
| **Buttons** |
| Lock Button | 11 | GPIO 17 | State Lock |
| Vol- Button | 16 | GPIO 23 | Volume Down |
| Vol+ Button | 18 | GPIO 24 | Volume Up |
| Play Button | 22 | GPIO 25 | Play/Pause |
| Common GND | 20 | - | Ground |

> **Note**: All buttons use internal pull-up resistors (configured in software)

## Software Requirements

### Operating System
- Raspberry Pi OS (Debian-based)
- Python 3.11+

### System Packages
Install required system packages:
```bash
sudo apt update
sudo apt install -y mpd mpc pulseaudio i2c-tools bluez sox python3-pip python3-venv
```

### Enable I2C
```bash
sudo raspi-config
# Navigate to: Interface Options -> I2C -> Enable
sudo reboot
```

### Python Dependencies
The project uses a virtual environment. Install Python packages:
```bash
cd ~/music-player
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**requirements.txt** should contain:
```
adafruit-blinka==8.x
adafruit-circuitpython-ssd1306==2.x
Pillow==10.x
RPi.GPIO==0.7.x
smbus2==0.4.x
numpy==1.24.x
```

## Music Setup

### Directory Structure
The system requires music to be organized in the MPD music directory:

```bash
/var/lib/mpd/music/
├── lowactivity/    # Calm music for staying still
├── walking/        # Moderate tempo for light walking
├── fastwalk/       # Upbeat music for brisk walking
└── running/        # High-energy music for running
```

### Adding Your Music

1. **Create directories** (if they don't exist):
```bash
sudo mkdir -p /var/lib/mpd/music/{lowactivity,walking,fastwalk,running}
```

2. **Copy your music files**:
```bash
# Example: copying music from ~/Music
sudo cp ~/Music/calm/* /var/lib/mpd/music/lowactivity/
sudo cp ~/Music/pop/* /var/lib/mpd/music/walking/
sudo cp ~/Music/upbeat/* /var/lib/mpd/music/fastwalk/
sudo cp ~/Music/rock/* /var/lib/mpd/music/running/
```

3. **Set proper permissions**:
```bash
sudo chown -R mpd:audio /var/lib/mpd/music/
sudo chmod -R 755 /var/lib/mpd/music/
```

4. **Update MPD database**:
```bash
mpc update
mpc ls  # Verify playlists are visible
```

### Supported Audio Formats
- MP3
- WAV
- FLAC
- OGG

## Bluetooth Setup

### Pair Your Earbuds

1. **Put earbuds in pairing mode**

2. **Scan and pair**:
```bash
bluetoothctl
> scan on
# Wait for your device to appear
> pair XX:XX:XX:XX:XX:XX
> trust XX:XX:XX:XX:XX:XX
> connect XX:XX:XX:XX:XX:XX
> exit
```

3. **Set as default audio sink**:
```bash
pactl list short sinks  # Find your Bluetooth sink
pactl set-default-sink bluez_output.XX_XX_XX_XX_XX_XX
```

## Running the System

### Manual Start
```bash
cd ~/music-player
source venv/bin/activate
./start.sh
```

### Stop the System
```bash
./stop.sh
```

### Enable Auto-start on Boot

Create systemd service:
```bash
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/music-assistant.service
```

Add the following content:
```ini
[Unit]
Description=Wearable Music Assistant
After=network.target sound.target bluetooth.target

[Service]
Type=simple
WorkingDirectory=/home/pi/music-player
ExecStart=/home/pi/music-player/start.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Enable and start:
```bash
systemctl --user enable music-assistant
systemctl --user start music-assistant
loginctl enable-linger pi  # Allow service to run without login
```

## Button Controls

| Button | Function |
|--------|----------|
| **Play/Pause** | Toggle music playback (manual override) |
| **Lock** | Lock current playlist (disable auto-switching) |
| **Vol+** | Increase volume |
| **Vol-** | Decrease volume |

## System Architecture

### Activity Detection Algorithm

1. **Sensor Reading** (100Hz):
   - 3-axis accelerometer data from MPU6050
   - Rolling window of 30 samples (0.3 seconds)

2. **Variance Calculation**:
   - Total variance = var(x) + var(y) + var(z)
   - Removes gravity component (orientation-independent)

3. **Classification Thresholds**:
   - **Staying Still**: variance ≤ 0.01
   - **Light Walking**: 0.01 < variance ≤ 0.03
   - **Brisk Walking**: 0.03 < variance ≤ 0.15
   - **Running**: variance > 0.15

4. **Hysteresis Filtering**:
   - 70 consecutive samples (0.7s) required for state change
   - Prevents false triggers during transitions

## Testing

The `tests/` directory contains validation scripts:

### Test Sensor
```bash
python3 tests/test_sensor.py
```
Validates MPU6050 I2C communication and displays real-time sensor data.

### Test Buttons
```bash
python3 tests/test_buttons.py
```
Validates GPIO button inputs with debouncing.

### Test OLED Display
```bash
python3 tests/test_oled.py
```
Tests OLED display functionality and I2C communication.

### Test Activity Detection
```bash
python3 tests/test_activity_detection.py
```
Shows real-time activity classification and variance values.

## Troubleshooting

### No Sound Output

**Check Bluetooth connection**:
```bash
bluetoothctl
> info XX:XX:XX:XX:XX:XX
> connect XX:XX:XX:XX:XX:XX
```

**Set default audio sink**:
```bash
pactl set-default-sink bluez_output.XX_XX_XX_XX_XX_XX
systemctl --user restart music-assistant
```

**Check MPD audio output**:
```bash
sudo nano /etc/mpd.conf
# Ensure audio_output is configured for PulseAudio/PipeWire
sudo systemctl restart mpd
```

### OLED Display Blank

**Check I2C connection**:
```bash
i2cdetect -y 1
# Should show device at address 0x3c
```

**Add user to i2c group**:
```bash
sudo usermod -aG i2c pi
sudo reboot
```

**Verify wiring**: Ensure SDA→GPIO2 (Pin 3), SCL→GPIO3 (Pin 5)

### Sensor Unresponsive

**Test sensor**:
```bash
python3 tests/test_sensor.py
```

**Check I2C**:
```bash
i2cdetect -y 1
# Should show device at address 0x68
```

**Check wiring**: Verify connections match pin table above

### Service Won't Auto-start

**Check service status**:
```bash
systemctl --user status music-assistant
```

**View logs**:
```bash
journalctl --user -u music-assistant -f
```

**Re-enable service**:
```bash
systemctl --user enable music-assistant
systemctl --user restart music-assistant
```

### Music Not Switching

**Verify playlists exist**:
```bash
mpc ls
# Should show: lowactivity, walking, fastwalk, running
```

**Update MPD database**:
```bash
mpc update
```

**Check activity detection**:
```bash
python3 tests/test_activity_detection.py
# Move device and observe state changes
```

### Permission Errors

**Fix music directory permissions**:
```bash
sudo chown -R mpd:audio /var/lib/mpd/music/
sudo chmod -R 755 /var/lib/mpd/music/
mpc update
```

**Fix GPIO permissions**:
```bash
sudo usermod -aG gpio pi
sudo reboot
```

## Project Structure

```
music-player/
├── src/                    # Source code
│   ├── main.py            # Main application
│   ├── activity.py        # Activity classifier
│   ├── music.py           # Music controller
│   ├── buttons.py         # Button handler
│   └── display.py         # OLED display manager
├── tests/                 # Test scripts
│   ├── test_sensor.py
│   ├── test_buttons.py
│   ├── test_oled.py
│   └── test_activity_detection.py
├── music/                 # Music directory (empty - placeholder)
├── venv/                  # Python virtual environment
├── start.sh               # Start script
├── stop.sh                # Stop script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Course Information
**Course**: ET4362E – Multimedia Embedded System  
**Institution**: Hanoi University of Science and Technology  
**School**: School of Electrical & Electronic Engineering  
**Instructor**: Dr. rer. nat. Tien Pham Van

## Authors
- **Nguyễn Quang Anh** (20213564) 
- **Trần Lê Hải Nam** (20213580) 
- **Hoàng Minh** (20213577) 

## License
This project is developed for educational purposes as part of the ET4362E course.

## Acknowledgments
- Dr. Tien Pham Van for project guidance
- Open-source communities for libraries and tools used in this project