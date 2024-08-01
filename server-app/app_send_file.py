import sys
import pico_util


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py <file_path>")
        sys.exit(1)
    file_path = sys.argv[1]

    pico_util.send_file_to_pico('/dev/tty.usbmodem1101', file_path)
    
