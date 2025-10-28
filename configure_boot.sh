#!/bin/bash

# configure_boot.sh
# Configures /boot/config.txt for FM Radio MP3 Player
# This script safely modifies boot configuration for I2S and SPI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Boot config file location (check both old and new Pi OS locations)
BOOT_CONFIG=""
if [ -f "/boot/firmware/config.txt" ]; then
    BOOT_CONFIG="/boot/firmware/config.txt"
    print_info "Found config at /boot/firmware/config.txt (Bookworm)"
elif [ -f "/boot/config.txt" ]; then
    BOOT_CONFIG="/boot/config.txt"
    print_info "Found config at /boot/config.txt (Bullseye or older)"
else
    print_error "Could not find boot config file!"
    print_error "Checked: /boot/firmware/config.txt and /boot/config.txt"
    exit 1
fi

BOOT_CONFIG_BACKUP="${BOOT_CONFIG}.backup-$(date +%Y%m%d-%H%M%S)"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}This script must be run with sudo${NC}"
    exit 1
fi

echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Boot Configuration Script              ║${NC}"
echo -e "${BLUE}║   FM Radio MP3 Player                    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if config file exists
if [ ! -f "$BOOT_CONFIG" ]; then
    print_error "Boot config file not found at $BOOT_CONFIG"
    exit 1
fi

# Create backup
print_info "Creating backup of $BOOT_CONFIG..."
cp "$BOOT_CONFIG" "$BOOT_CONFIG_BACKUP"
print_status "Backup created: $BOOT_CONFIG_BACKUP"
echo ""

# Function to add or update a configuration line
add_or_update_config() {
    local param=$1
    local value=$2
    local comment=$3
    
    # Check if parameter exists (enabled)
    if grep -q "^${param}=${value}" "$BOOT_CONFIG"; then
        print_status "${param}=${value} already set"
        return 0
    fi
    
    # Check if parameter exists but is disabled (commented out)
    if grep -q "^#${param}=" "$BOOT_CONFIG"; then
        print_info "Updating existing ${param} parameter..."
        sed -i "s/^#${param}=.*/${param}=${value}/" "$BOOT_CONFIG"
        print_status "${param}=${value} updated"
        return 0
    fi
    
    # Check if parameter exists with different value
    if grep -q "^${param}=" "$BOOT_CONFIG"; then
        print_info "Changing ${param} value..."
        sed -i "s/^${param}=.*/${param}=${value}/" "$BOOT_CONFIG"
        print_status "${param}=${value} changed"
        return 0
    fi
    
    # Parameter doesn't exist, add it with comment
    print_info "Adding ${param}=${value}..."
    echo "" >> "$BOOT_CONFIG"
    if [ -n "$comment" ]; then
        echo "# $comment" >> "$BOOT_CONFIG"
    fi
    echo "${param}=${value}" >> "$BOOT_CONFIG"
    print_status "${param}=${value} added"
}

# Function to add overlay if not present
add_overlay() {
    local overlay=$1
    local comment=$2
    
    if grep -q "^dtoverlay=${overlay}" "$BOOT_CONFIG"; then
        print_status "dtoverlay=${overlay} already present"
        return 0
    fi
    
    if grep -q "^#dtoverlay=${overlay}" "$BOOT_CONFIG"; then
        print_info "Enabling dtoverlay=${overlay}..."
        sed -i "s/^#dtoverlay=${overlay}/dtoverlay=${overlay}/" "$BOOT_CONFIG"
        print_status "dtoverlay=${overlay} enabled"
        return 0
    fi
    
    print_info "Adding dtoverlay=${overlay}..."
    if [ -n "$comment" ]; then
        echo "# $comment" >> "$BOOT_CONFIG"
    fi
    echo "dtoverlay=${overlay}" >> "$BOOT_CONFIG"
    print_status "dtoverlay=${overlay} added"
}

# Disable built-in audio (conflicts with I2S)
print_info "Configuring audio settings..."
if grep -q "^dtparam=audio=on" "$BOOT_CONFIG"; then
    sed -i 's/^dtparam=audio=on/dtparam=audio=off/' "$BOOT_CONFIG"
    print_status "Built-in audio disabled"
elif grep -q "^dtparam=audio=off" "$BOOT_CONFIG"; then
    print_status "Built-in audio already disabled"
else
    add_or_update_config "dtparam=audio" "off" "Disable built-in audio"
fi
echo ""

# Enable SPI
print_info "Enabling SPI interface..."
add_or_update_config "dtparam=spi" "on" "Enable SPI for display"
echo ""

# Enable I2S
print_info "Enabling I2S interface..."
add_or_update_config "dtparam=i2s" "on" "Enable I2S for audio DAC"
echo ""

# Add HiFiBerry DAC overlay for PCM5102
print_info "Configuring I2S DAC (PCM5102)..."
# Check if FM Radio section already exists
if ! grep -q "# FM Radio MP3 Player Configuration" "$BOOT_CONFIG"; then
    echo "" >> "$BOOT_CONFIG"
    echo "# FM Radio MP3 Player Configuration" >> "$BOOT_CONFIG"
    echo "# I2S Audio DAC (PCM5102)" >> "$BOOT_CONFIG"
fi
add_overlay "hifiberry-dac" "HiFiBerry DAC overlay for PCM5102"
echo ""

# Show summary
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Configuration Complete!                ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Changes made:${NC}"
echo "  • Built-in audio: disabled"
echo "  • SPI interface: enabled"
echo "  • I2S interface: enabled"
echo "  • HiFiBerry DAC overlay: added"
echo ""
echo -e "${YELLOW}Backup created:${NC}"
echo "  $BOOT_CONFIG_BACKUP"
echo ""
echo -e "${YELLOW}To restore original configuration:${NC}"
echo "  sudo cp $BOOT_CONFIG_BACKUP $BOOT_CONFIG"
echo ""
echo -e "${RED}⚠ REBOOT REQUIRED${NC}"
echo "  Changes will take effect after reboot"
echo "  Run: sudo reboot"
echo ""

exit 0
