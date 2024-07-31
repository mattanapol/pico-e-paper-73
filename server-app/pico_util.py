import serial
import time
import struct
import os

def send_file_to_pico(serial_port, file_path, pico_save_file_path = ""):
    with serial.Serial(serial_port, 115200, timeout=1) as ser:
        time.sleep(2)  # wait for the Pico to initialize

        try:
            with open(file_path, 'rb') as file:
                # Extract the file name and size
                file_name = os.path.basename(file_path)
                file_size = len(file.read())
                file.seek(0)  # Reset file pointer to beginning
                # Ensure the file name fits into 256 bytes
                if len(file_name) > 100:
                    raise ValueError("File name is too long. It must be 100 characters or less.")
                
                # path combine
                if pico_save_file_path:
                    file_name = os.path.join(pico_save_file_path, file_name)

                # Create the header
                header = struct.pack('256sI', file_name.encode('utf-8'), file_size)
                # Send the header
                ser.write(header)
                print(f"Sending file {file_name} ({file_size} bytes)...")

                sent_bytes = 0
                progress = 0
                while True:
                    data = file.read(1024)  # Read in chunks of 1024 bytes
                    if not data:
                        break
                    ser.write(data)
                    sent_bytes += len(data)
                    new_progress = int((sent_bytes / file_size) * 100)
                    if new_progress > progress:
                        progress = new_progress
                        print(f"Progress: {progress}%", end="\r")
                    time.sleep(0.020)
                print("File sent successfully.")
        except FileNotFoundError:
            print("\nFile not found.")
        except serial.SerialException as e:
            print("\nSerial port error:", e)