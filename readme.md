# Raspberry pi Pico for Waveshare E-paper

## Firmware for Raspberry pi Pico
This based on original example firmware provided by Waveshare.
But this modified version include logic that support file streaming from USB device and store it to TF card mounted to the board.

Ref: https://www.waveshare.com/wiki/PhotoPainter



## Server application that feed data to 
Desktop application in python, tested on Macbook M1.
### Functional
1. Fetch calendar events from google api(personal calendar and shared calendar)
2. Create png image 800x480 pixels of calendar entries(tested on Macbook)
3. Convert png image to bmp image that Pico support
4. Send file through serial port
5. Read data from serial port