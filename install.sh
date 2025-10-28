#!/bin/bash

# FM Radio MP3 Player Installation Script
# For Raspberry Pi Zero 2 W

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════╗"
echo "║   FM Radio MP3 Player Installer          ║"
echo "║   Raspberry Pi Zero 2 W                  ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run with sudo: sudo ./install.sh${NC}"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER=${SUDO_USER:-$USER}
USER_HOME=$(eval echo ~$ACTUAL_USER)

echo -e "${YELLOW}Installing for user: $ACTUAL_USER${NC}"
echo -e "${YELLOW}Home directory: $USER_HOME${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

# Update system
print_info "Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq
print_status "System updated"

# Install required packages
print_info "Installing required packages..."
apt-get install -y -qq \
    python3-pip \
    python3-dev \
    python3-pil \
    python3-numpy \
    python3-spidev \
    python3-rpi.gpio \
    python3-pygame \
    python3-gpiozero \
    git \
    vim

print_status "Packages installed"

# Install Python packages via pip
print_info "Installing Python packages..."
pip3 install --quiet pillow spidev pygame RPi.GPIO gpiozero
print_status "Python packages installed"

# Enable SPI
print_info "Enabling SPI interface..."
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" >> /boot/config.txt
    print_status "SPI enabled"
else
    print_status "SPI already enabled"
fi

# Configure I2S Audio
print_info "Configuring I2S audio..."

# Disable built-in audio
if grep -q "^dtparam=audio=on" /boot/config.txt; then
    sed -i 's/^dtparam=audio=on/dtparam=audio=off/' /boot/config.txt
fi

# Add I2S configuration if not present
if ! grep -q "^dtparam=i2s=on" /boot/config.txt; then
    cat >> /boot/config.txt << EOF

# I2S Audio Configuration for PCM5102
dtparam=audio=off
dtparam=i2s=on
dtoverlay=hifiberry-dac
EOF
    print_status "I2S configuration added"
else
    print_status "I2S already configured"
fi

# Configure ALSA audio
print_info "Configuring ALSA..."
if [ -f "config/asound.conf" ]; then
    cp config/asound.conf /etc/asound.conf
    print_status "ALSA configured"
else
    cat > /etc/asound.conf << EOF
pcm.!default {
    type hw
    card 0
}

ctl.!default {
    type hw
    card 0
}
EOF
    print_status "ALSA configuration created"
fi

# Create music directory
print_info "Creating music directory..."
MUSIC_DIR="$USER_HOME/music"
mkdir -p "$MUSIC_DIR"
chown $ACTUAL_USER:$ACTUAL_USER "$MUSIC_DIR"

# Create example playlist folders
mkdir -p "$MUSIC_DIR/Rock"
mkdir -p "$MUSIC_DIR/Jazz"
mkdir -p "$MUSIC_DIR/Classical"
chown -R $ACTUAL_USER:$ACTUAL_USER "$MUSIC_DIR"
print_status "Music directory created at $MUSIC_DIR"

# Copy main application
print_info "Installing FM Radio Player application..."
if [ -f "fm_radio_player.py" ]; then
    cp fm_radio_player.py "$USER_HOME/fm_radio_player.py"
    chown $ACTUAL_USER:$ACTUAL_USER "$USER_HOME/fm_radio_player.py"
    chmod +x "$USER_HOME/fm_radio_player.py"
    print_status "Application installed"
else
    print_error "fm_radio_player.py not found!"
    exit 1
fi

# Ask about auto-start
echo ""
read -p "Enable auto-start on boot? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Setting up systemd service..."
    
    # Create systemd service file
    cat > /etc/systemd/system/fm-radio.service << EOF
[Unit]
Description=FM Radio MP3 Player
After=network.target sound.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$USER_HOME
ExecStart=/usr/bin/python3 $USER_HOME/fm_radio_player.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable fm-radio.service
    print_status "Auto-start enabled"
else
    print_info "Auto-start not enabled"
fi

# Installation complete
echo ""
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════╗"
echo "║   Installation Complete!                 ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Add MP3 files to $MUSIC_DIR"
echo "   - Create folders for each playlist/station"
echo "   - Add MP3 files to each folder"
echo ""
echo "2. Reboot your Raspberry Pi:"
echo "   sudo reboot"
echo ""
echo "3. After reboot, check status:"
echo "   sudo systemctl status fm-radio.service"
echo ""
echo -e "${YELLOW}Manual Control:${NC}"
echo "   Start:   sudo systemctl start fm-radio.service"
echo "   Stop:    sudo systemctl stop fm-radio.service"
echo "   Restart: sudo systemctl restart fm-radio.service"
echo "   Logs:    sudo journalctl -u fm-radio.service -f"
echo ""
echo -e "${YELLOW}Manual Run (for testing):${NC}"
echo "   python3 $USER_HOME/fm_radio_player.py"
echo ""
echo -e "${GREEN}Enjoy your FM Radio Player! 📻${NC}"
