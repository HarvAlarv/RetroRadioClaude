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

| Encoder Pin | RPi Pin | GPIO | Description |
|-------------|---------|------|-------------|
| + | Pin 17 | 3.3V | Power |
| GND | Pin 14 | GND | Ground |
| SW | Pin 15 | GPIO 22 | Button Switch |
| DT | Pin 12 | GPIO 18 | Data |
| CLK | Pin 11 | GPIO 17 | Clock |

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
