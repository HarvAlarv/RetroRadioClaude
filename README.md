# FM Radio Style MP3 Player for Raspberry Pi

A vintage FM radio-inspired MP3 player built with Raspberry Pi Zero 2 W. Turn the knob to browse "stations" (playlists), click to select, and enjoy shuffled playback through a round display and I2S DAC.

![Raspberry Pi FM Radio](https://img.shields.io/badge/Raspberry%20Pi-Zero%202%20W-C51A4A?logo=raspberry-pi)
![Python](https://img.shields.io/badge/Python-3.7+-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- 🎵 Folder-based playlists act as "radio stations"
- 🔄 Shuffled playback with no repeats until all songs played
- 🎛️ Rotary encoder for browsing and selecting stations
- 📺 Round GC9A01 display shows station names
- 🔊 High-quality I2S audio output via PCM5102 DAC
- 🚀 Auto-start on boot option

## Hardware Requirements

- Raspberry Pi Zero 2 W
- GY-PCM5102 I2S DAC module
- KY-040 Rotary Encoder with button
- GC9A01 1.28" round LCD display (240x240)
- External amplifier/speakers
- MicroSD card (8GB+)
- Power supply (5V 2.5A recommended)

## Quick Start

### 1. Hardware Setup

See [HARDWARE.md](docs/HARDWARE.md) for detailed wiring diagrams.

### 2. Software Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/fm-radio-mp3-player.git
cd fm-radio-mp3-player

# Run the installer
chmod +x install.sh
sudo ./install.sh
```

The installer will:
- Configure I2S audio
- Enable SPI interface
- Install all dependencies
- Set up the music directory
- Optionally enable auto-start

### 3. Add Your Music
```bash
# Create playlist folders (stations)
mkdir -p ~/music/Rock
mkdir -p ~/music/Jazz
mkdir -p ~/music/Classical

# Add MP3 files to each folder
cp /path/to/your/rock/songs/*.mp3 ~/music/Rock/
cp /path/to/your/jazz/songs/*.mp3 ~/music/Jazz/
```

### 4. Run the Player
```bash
# Manual start
python3 fm_radio_player.py

# Or if auto-start enabled, just reboot
sudo reboot
```

## Usage

- **Browse Stations**: Rotate the encoder knob
- **Select Station**: Press the encoder button
- **Volume Control**: Use external amplifier

## Configuration

Edit `fm_radio_player.py` to customize:
```python
MUSIC_DIR = "/home/pi/music"  # Music directory location
DISPLAY_DC_PIN = 25           # GPIO pins
DISPLAY_RST_PIN = 27
DISPLAY_CS_PIN = 8
ROTARY_CLK_PIN = 17
ROTARY_DT_PIN = 18
ROTARY_SW_PIN = 22
```

## Troubleshooting

### No Audio Output
```bash
# Check I2S device
aplay -l

# Test audio
speaker-test -c2 -t wav
```

### Display Not Working
```bash
# Verify SPI enabled
ls /dev/spidev*

# Check service status
sudo systemctl status fm-radio.service
```

### View Logs
```bash
sudo journalctl -u fm-radio.service -f
```

## System Control
```bash
# Start service
sudo systemctl start fm-radio.service

# Stop service
sudo systemctl stop fm-radio.service

# Restart service
sudo systemctl restart fm-radio.service

# Disable auto-start
sudo systemctl disable fm-radio.service
```

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python, pygame, and gpiozero
- Inspired by vintage FM radio aesthetics
- Thanks to the Raspberry Pi community

## Future Enhancements

- [ ] Album art display
- [ ] Bluetooth connectivity
- [ ] Web interface for remote control
- [ ] EQ controls
- [ ] Sleep timer
- [ ] Station favorites

---

**Enjoy your retro FM radio experience!** 📻
