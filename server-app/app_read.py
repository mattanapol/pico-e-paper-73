import serial
import time

def read_serial_port(port, baudrate):
  with serial.Serial(port, baudrate) as ser:
    while True:
      try:
        data = ser.readline().decode('utf-8').rstrip()
        if data:
          print(f"Received: {data}")
      except Exception as e:
        print(e)
        time.sleep(1)

if __name__ == "__main__":
    import os  # Import for os.path.getsize

    read_serial_port('/dev/tty.usbmodem1101', 115200)