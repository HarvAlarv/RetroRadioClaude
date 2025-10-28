# Hardware Setup Guide

## Components Required

- Raspberry Pi Zero 2 W
- GY-PCM5102 I2S DAC Module
- KY-040 Rotary Encoder with Button
- GC9A01 1.28" Round LCD Display (240x240)
- External Amplifier with Speakers
- MicroSD Card (8GB minimum)
- 5V 2.5A Power Supply
- Jumper Wires

## Wiring Diagrams

### GY-PCM5102 I2S DAC

Connect to Raspberry Pi GPIO header:

| PCM5102 Pin | RPi Pin | GPIO | Description |
|-------------|---------|------|-------------|
| VCC | Pin 1 | 3.3V | Power |
| GND | Pin 6 | GND | Ground |
| BCK | Pin 12 | GPIO 18 | Bit Clock |
| DIN | Pin 40 | GPIO 21 | Data In |
| LCK | Pin 35 | GPIO 19 | Word Clock |
| SCK | GND | - | Short to GND |
| FMT | GND | - | Short to GND |

**Note**: SCK and FMT must be connected to GND for I2S mode.

### KY-040 Rotary Encoder

**⚠️ IMPORTANT: GPIO 23 used for DT to avoid conflict with I2S on GPIO 18**

| Encoder Pin | RPi Pin | GPIO | Description |
|-------------|---------|------|-------------|
| + | Pin 17 | 3.3V | Power |
| GND | Pin 14 | GND | Ground |
| SW | Pin 15 | GPIO 22 | Button Switch |
| DT | Pin 16 | GPIO 23 | Data (Changed from GPIO 18) |
| CLK | Pin 11 | GPIO 17 | Clock |

**Critical Note:** Originally GPIO 18 was planned for encoder DT, but this conflicts with the I2S DAC BCK signal. We use GPIO 23 instead.

### GC9A01 Round Display

| Display Pin | RPi Pin | GPIO | Description |
|-------------|---------|------|-------------|
| GND | Pin 20 | GND | Ground |
| VCC | Pin 17 | 3.3V | Power |
| SCL | Pin 23 | GPIO 11 | SPI Clock |
| SDA | Pin 19 | GPIO 10 | SPI MOSI |
| RES | Pin 13 | GPIO 27 | Reset |
| DC | Pin 22 | GPIO 25 | Data/Command |
| CS | Pin 24 | GPIO 8 | Chip Select |
| BL | Pin 1 | 3.3V | Backlight |

## GPIO Pin Reference

```
Raspberry Pi Zero 2 W GPIO Header

     3.3V [ 1] [ 2] 5V
GPIO  2 [ 3] [ 4] 5V
GPIO  3 [ 5] [ 6] GND
GPIO  4 [ 7] [ 8] GPIO 14
      GND [ 9] [10] GPIO 15
GPIO 17 [11] [12] GPIO 18  ← I2S BCK (DAC)
GPIO 27 [13] [14] GND
GPIO 22 [15] [16] GPIO 23  ← Encoder DT
     3.3V [17] [18] GPIO 24
GPIO 10 [19] [20] GND
GPIO  9 [21] [22] GPIO 25
GPIO 11 [23] [24] GPIO 8
      GND [25] [26] GPIO 7
GPIO  0 [27] [28] GPIO 1
GPIO  5 [29] [30] GND
GPIO  6 [31] [32] GPIO 12
GPIO 13 [33] [34] GND
GPIO 19 [35] [36] GPIO 16  ← I2S LCK (DAC)
GPIO 26 [37] [38] GPIO 20
      GND [39] [40] GPIO 21  ← I2S DIN (DAC)
```

## GPIO Usage Summary

| GPIO | Device | Function |
|------|--------|----------|
| 8 | Display | Chip Select |
| 10 | Display | SPI MOSI |
| 11 | Display | SPI Clock |
| 17 | Encoder | Clock |
| 18 | I2S DAC | Bit Clock |
| 19 | I2S DAC | Word Clock |
| 21 | I2S DAC | Data In |
| 22 | Encoder | Button |
| 23 | Encoder | Data |
| 25 | Display | Data/Command |
| 27 | Display | Reset |

## Assembly Tips

1. **Use a breadboard** during initial testing
2. **Double-check connections** before powering on
3. **Test each component individually** before full assembly
4. **Use short wires** to minimize interference
5. **Secure all connections** to prevent intermittent issues
6. **Verify GPIO assignments** match the code configuration

## Audio Output

The PCM5102 DAC outputs line-level audio:
- Connect to an external amplifier
- Use powered speakers
- Or connect to a stereo system AUX input

**Do NOT** connect directly to passive speakers - you need amplification!

## Power Considerations

- Raspberry Pi Zero 2 W needs 5V 2.5A minimum
- Total current draw: ~1-1.5A typical
- Use quality power supply to avoid audio noise
- Consider using ferrite beads on power cables

## Troubleshooting Hardware

### Display Issues
- Verify 3.3V power (NOT 5V!)
- Check SPI connections
- Ensure CS, DC, and RST pins are correct
- Try reducing SPI speed in code

### Audio Issues
- Verify SCK and FMT are grounded on PCM5102
- Check I2S pin connections (GPIO 18, 19, 21)
- Ensure DAC is getting 3.3V
- Test with headphones first
- Verify no GPIO conflicts

### Encoder Issues
- Check pull-up resistors (usually built-in)
- Verify CLK is on GPIO 17 and DT is on GPIO 23
- Ensure button (SW) is on GPIO 22
- Add debouncing capacitor if needed (0.1µF)

### GPIO Conflict Warning
⚠️ **Do NOT use GPIO 18 for the encoder** - it's required by the I2S DAC. The encoder DT must be on GPIO 23 as shown in this guide.

## Enclosure Recommendations

- **3D Printed Case**: Design around round display
- **Vintage Radio Case**: Gut old radio for authentic look
- **Acrylic Box**: Show off the components
- **Wood Box**: Classic, warm aesthetic

## Safety Notes

⚠️ **Important Safety Information:**
- Never connect 5V to 3.3V components
- Always power off before making connections
- Check polarity on all connections
- Use proper gauge wire for power
- Avoid shorting GPIO pins
- Keep away from water and moisture

## Verification Checklist

Before powering on:
- [ ] All 3.3V connections verified (not 5V)
- [ ] All ground connections secure
- [ ] No GPIO pin conflicts (especially GPIO 18)
- [ ] PCM5102 SCK and FMT shorted to GND
- [ ] Display CS, DC, RST connected correctly
- [ ] Encoder on correct pins (CLK=17, DT=23, SW=22)
- [ ] No loose wires or shorts

---

**Need Help?** Check the main README or open an issue on GitHub.
