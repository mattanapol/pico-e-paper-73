import serial
import time

def read_serial_port(port, baudrate):
  with serial.Serial(port, baudrate) as ser:
    while True:
      try:
        data = ser.read()
        if data:
          print(f"Received[{len(data)}]: {data.decode('utf-8').rstrip()}")
      except Exception as e:
        print(f"error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    import os  # Import for os.path.getsize

    # read_serial_port('/dev/tty.usbmodem1101', 115200)
    read_serial_port('/dev/tty.usbserial-A5069RR4', 115200)