#!/usr/bin/env python3
"""
FM Radio Style MP3 Player for Raspberry Pi Zero 2 W
Main application file
"""

import os
import sys
import time
import random
from pathlib import Path
from typing import List, Optional
import pygame
from gpiozero import RotaryEncoder, Button
from PIL import Image, ImageDraw, ImageFont
import spidev
import RPi.GPIO as GPIO

# ==================== CONFIGURATION ====================
MUSIC_DIR = "/home/pi/music"  # Root directory containing playlist folders
DISPLAY_SPI_BUS = 0
DISPLAY_SPI_DEVICE = 0
DISPLAY_DC_PIN = 25
DISPLAY_RST_PIN = 27
DISPLAY_CS_PIN = 8
ROTARY_CLK_PIN = 17
ROTARY_DT_PIN = 23  # Changed from 18 to avoid conflict with I2S BCK on GPIO 18
ROTARY_SW_PIN = 22
DISPLAY_TIMEOUT = 30  # Seconds before dimming display when idle

# ==================== GC9A01 DISPLAY DRIVER ====================
class GC9A01:
    """Driver for GC9A01 240x240 round LCD display"""
    
    def __init__(self, spi_bus=0, spi_device=0, dc_pin=25, rst_pin=27, cs_pin=8):
        self.width = 240
        self.height = 240
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.cs_pin = cs_pin
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        
        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 32000000
        self.spi.mode = 0
        
        self.reset()
        self.init_display()
        
    def reset(self):
        """Hardware reset"""
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.12)
        
    def write_cmd(self, cmd):
        """Write command to display"""
        GPIO.output(self.dc_pin, GPIO.LOW)
        GPIO.output(self.cs_pin, GPIO.LOW)
        self.spi.writebytes([cmd])
        GPIO.output(self.cs_pin, GPIO.HIGH)
        
    def write_data(self, data):
        """Write data to display"""
        GPIO.output(self.dc_pin, GPIO.HIGH)
        GPIO.output(self.cs_pin, GPIO.LOW)
        if isinstance(data, int):
            self.spi.writebytes([data])
        else:
            self.spi.writebytes(data)
        GPIO.output(self.cs_pin, GPIO.HIGH)
        
    def init_display(self):
        """Initialize display with configuration commands"""
        commands = [
            (0xEF, []),
            (0xEB, [0x14]),
            (0xFE, []),
            (0xEF, []),
            (0xEB, [0x14]),
            (0x84, [0x40]),
            (0x85, [0xFF]),
            (0x86, [0xFF]),
            (0x87, [0xFF]),
            (0x88, [0x0A]),
            (0x89, [0x21]),
            (0x8A, [0x00]),
            (0x8B, [0x80]),
            (0x8C, [0x01]),
            (0x8D, [0x01]),
            (0x8E, [0xFF]),
            (0x8F, [0xFF]),
            (0xB6, [0x00, 0x00]),
            (0x36, [0x48]),
            (0x3A, [0x05]),
            (0x90, [0x08, 0x08, 0x08, 0x08]),
            (0xBD, [0x06]),
            (0xBC, [0x00]),
            (0xFF, [0x60, 0x01, 0x04]),
            (0xC3, [0x13]),
            (0xC4, [0x13]),
            (0xC9, [0x22]),
            (0xBE, [0x11]),
            (0xE1, [0x10, 0x0E]),
            (0xDF, [0x21, 0x0c, 0x02]),
            (0xF0, [0x45, 0x09, 0x08, 0x08, 0x26, 0x2A]),
            (0xF1, [0x43, 0x70, 0x72, 0x36, 0x37, 0x6F]),
            (0xF2, [0x45, 0x09, 0x08, 0x08, 0x26, 0x2A]),
            (0xF3, [0x43, 0x70, 0x72, 0x36, 0x37, 0x6F]),
            (0xED, [0x1B, 0x0B]),
            (0xAE, [0x77]),
            (0xCD, [0x63]),
            (0x70, [0x07, 0x07, 0x04, 0x0E, 0x0F, 0x09, 0x07, 0x08, 0x03]),
            (0xE8, [0x34]),
            (0x62, [0x18, 0x0D, 0x71, 0xED, 0x70, 0x70, 0x18, 0x0F, 0x71, 0xEF, 0x70, 0x70]),
            (0x63, [0x18, 0x11, 0x71, 0xF1, 0x70, 0x70, 0x18, 0x13, 0x71, 0xF3, 0x70, 0x70]),
            (0x64, [0x28, 0x29, 0xF1, 0x01, 0xF1, 0x00, 0x07]),
            (0x66, [0x3C, 0x00, 0xCD, 0x67, 0x45, 0x45, 0x10, 0x00, 0x00, 0x00]),
            (0x67, [0x00, 0x3C, 0x00, 0x00, 0x00, 0x01, 0x54, 0x10, 0x32, 0x98]),
            (0x74, [0x10, 0x85, 0x80, 0x00, 0x00, 0x4E, 0x00]),
            (0x98, [0x3e, 0x07]),
            (0x35, []),
            (0x21, []),
            (0x11, []),
        ]
        
        for cmd, data in commands:
            self.write_cmd(cmd)
            if data:
                for byte in data:
                    self.write_data(byte)
            time.sleep(0.001)
            
        time.sleep(0.12)
        self.write_cmd(0x29)  # Display on
        
    def set_window(self, x0, y0, x1, y1):
        """Set drawing window"""
        self.write_cmd(0x2A)
        self.write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self.write_cmd(0x2B)
        self.write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        self.write_cmd(0x2C)
        
    def display_image(self, image):
        """Display PIL Image on screen"""
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        self.set_window(0, 0, self.width - 1, self.height - 1)
        
        # Convert to RGB565 and send
        pixels = []
        for y in range(self.height):
            for x in range(self.width):
                r, g, b = image.getpixel((x, y))
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                pixels.append(rgb565 >> 8)
                pixels.append(rgb565 & 0xFF)
        
        GPIO.output(self.dc_pin, GPIO.HIGH)
        GPIO.output(self.cs_pin, GPIO.LOW)
        self.spi.writebytes(pixels)
        GPIO.output(self.cs_pin, GPIO.HIGH)
        
    def clear(self, color=(0, 0, 0)):
        """Clear screen with color"""
        image = Image.new('RGB', (self.width, self.height), color)
        self.display_image(image)

# ==================== PLAYLIST MANAGER ====================
class PlaylistManager:
    """Manages folder-based playlists with shuffle playback"""
    
    def __init__(self, music_dir):
        self.music_dir = Path(music_dir)
        self.playlists = []
        self.current_playlist_idx = 0
        self.current_track_queue = []
        self.scan_playlists()
        
    def scan_playlists(self):
        """Scan music directory for folders containing MP3 files"""
        self.playlists = []
        
        if not self.music_dir.exists():
            print(f"Music directory {self.music_dir} does not exist!")
            return
            
        for folder in sorted(self.music_dir.iterdir()):
            if folder.is_dir():
                mp3_files = list(folder.glob("*.mp3"))
                if mp3_files:
                    self.playlists.append({
                        'name': folder.name,
                        'path': folder,
                        'tracks': [str(f) for f in mp3_files]
                    })
        
        print(f"Found {len(self.playlists)} playlists")
        
    def get_playlist_names(self):
        """Get list of playlist names"""
        return [p['name'] for p in self.playlists]
    
    def get_current_playlist_name(self):
        """Get current playlist name"""
        if self.playlists:
            return self.playlists[self.current_playlist_idx]['name']
        return "No Playlists"
    
    def next_playlist(self):
        """Move to next playlist"""
        if self.playlists:
            self.current_playlist_idx = (self.current_playlist_idx + 1) % len(self.playlists)
            
    def prev_playlist(self):
        """Move to previous playlist"""
        if self.playlists:
            self.current_playlist_idx = (self.current_playlist_idx - 1) % len(self.playlists)
            
    def start_playlist(self):
        """Start playing current playlist - create shuffled queue"""
        if not self.playlists:
            return None
            
        playlist = self.playlists[self.current_playlist_idx]
        self.current_track_queue = playlist['tracks'].copy()
        random.shuffle(self.current_track_queue)
        
        return self.get_next_track()
    
    def get_next_track(self):
        """Get next track from queue"""
        if self.current_track_queue:
            return self.current_track_queue.pop(0)
        else:
            # Queue exhausted, reshuffle and continue
            return self.start_playlist()

# ==================== MP3 PLAYER ====================
class MP3Player:
    """Handles MP3 playback using pygame mixer"""
    
    def __init__(self):
        pygame.mixer.init()
        self.playing = False
        self.current_track = None
        
    def play(self, track_path):
        """Play an MP3 file"""
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.playing = True
            self.current_track = track_path
            print(f"Playing: {os.path.basename(track_path)}")
        except Exception as e:
            print(f"Error playing {track_path}: {e}")
            self.playing = False
            
    def stop(self):
        """Stop playback"""
        pygame.mixer.music.stop()
        self.playing = False
        self.current_track = None
        
    def is_playing(self):
        """Check if music is playing"""
        return pygame.mixer.music.get_busy()

# ==================== MAIN APPLICATION ====================
class FMRadioPlayer:
    """Main application coordinating all components"""
    
    def __init__(self):
        print("Initializing FM Radio Player...")
        
        # Initialize components
        self.display = GC9A01(DISPLAY_SPI_BUS, DISPLAY_SPI_DEVICE, 
                              DISPLAY_DC_PIN, DISPLAY_RST_PIN, DISPLAY_CS_PIN)
        self.playlist_mgr = PlaylistManager(MUSIC_DIR)
        self.player = MP3Player()
        
        # State
        self.browsing = False
        self.last_interaction = time.time()
        self.running = True
        
        # Setup rotary encoder
        self.encoder = RotaryEncoder(ROTARY_CLK_PIN, ROTARY_DT_PIN, wrap=False, max_steps=1000)
        self.button = Button(ROTARY_SW_PIN, pull_up=True, bounce_time=0.1)
        self.encoder.when_rotated_clockwise = self.on_rotate_cw
        self.encoder.when_rotated_counter_clockwise = self.on_rotate_ccw
        self.button.when_pressed = self.on_button_press
        
        # Start with first playlist
        if self.playlist_mgr.playlists:
            self.start_playback()
        else:
            self.show_message("No Music Found")
            
    def on_rotate_cw(self):
        """Handle clockwise rotation"""
        self.browsing = True
        self.last_interaction = time.time()
        self.playlist_mgr.next_playlist()
        self.show_playlist_name(self.playlist_mgr.get_current_playlist_name())
        
    def on_rotate_ccw(self):
        """Handle counter-clockwise rotation"""
        self.browsing = True
        self.last_interaction = time.time()
        self.playlist_mgr.prev_playlist()
        self.show_playlist_name(self.playlist_mgr.get_current_playlist_name())
        
    def on_button_press(self):
        """Handle button press - select playlist"""
        self.last_interaction = time.time()
        if self.browsing:
            self.browsing = False
            self.start_playback()
            
    def start_playback(self):
        """Start playing selected playlist"""
        self.player.stop()
        track = self.playlist_mgr.start_playlist()
        if track:
            self.player.play(track)
            self.show_playlist_name(self.playlist_mgr.get_current_playlist_name())
            
    def show_playlist_name(self, name):
        """Display playlist name on screen"""
        # Create image
        image = Image.new('RGB', (240, 240), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Try to load a nice font, fall back to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except:
            font = ImageFont.load_default()
        
        # Word wrap text
        words = name.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= 200:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw text centered
        y_offset = 120 - (len(lines) * 20)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (240 - text_width) // 2
            draw.text((x, y_offset), line, fill=(255, 255, 255), font=font)
            y_offset += 35
        
        self.display.display_image(image)
        
    def show_message(self, message):
        """Show a message on display"""
        image = Image.new('RGB', (240, 240), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
            
        bbox = draw.textbbox((0, 0), message, font=font)
        text_width = bbox[2] - bbox[0]
        x = (240 - text_width) // 2
        y = 110
        
        draw.text((x, y), message, fill=(255, 255, 255), font=font)
        self.display.display_image(image)
        
    def run(self):
        """Main loop"""
        print("FM Radio Player running...")
        
        try:
            while self.running:
                # Check if track finished and start next
                if not self.browsing and not self.player.is_playing():
                    track = self.playlist_mgr.get_next_track()
                    if track:
                        self.player.play(track)
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources"""
        self.player.stop()
        GPIO.cleanup()
        pygame.mixer.quit()

# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    # Ensure music directory exists
    if not os.path.exists(MUSIC_DIR):
        print(f"Creating music directory: {MUSIC_DIR}")
        os.makedirs(MUSIC_DIR)
        print("Please add folders with MP3 files to this directory")
        sys.exit(1)
    
    player = FMRadioPlayer()
    player.run()
