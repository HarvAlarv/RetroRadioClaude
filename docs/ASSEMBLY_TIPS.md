## Assembly Tips

1. **Use a breadboard** during initial testing
2. **Double-check connections** before powering on
3. **Test each component individually** before full assembly
4. **Use short wires** to minimize interference
5. **Secure all connections** to prevent intermittent issues

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
- Verify SCK and FMT are grounded
- Check I2S pin connections
- Ensure DAC is getting 3.3V
- Test with headphones first

### Encoder Issues
- Check pull-up resistors (usually built-in)
- Verify CLK and DT aren't swapped
- Add debouncing capacitor if needed (0.1µF)

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

---

**Need Help?** Check the main README or open an issue on GitHub.
