import serial
import time

def read_serial_port(port, baudrate):
  with serial.Serial(port, baudrate) as ser:
    while True:
      try:
        # ser.write(b'Hello from Python\n')
        data = ser.read_all()
        if data:
          print(f"Received[{len(data)}]: {data.decode('utf-8').rstrip()}")
      except Exception as e:
        print(f"error: {e}")
        print(f"Received[{len(data)}](raw): {data}")
      time.sleep(0.1)

if __name__ == "__main__":
    import os  # Import for os.path.getsize

    # read_serial_port('/dev/tty.usbmodem1101', 115200)
    read_serial_port('/dev/cu.usbmodem58760914231', 115200)
    # read_serial_port('/dev/tty.usbserial-A5069RR4', 115200)
    # read_serial_port('/dev/cu.usbmodem595B0062961', 115200)