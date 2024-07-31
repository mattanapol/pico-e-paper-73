import sys
import convert
import pico_util


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py <file_path>")
        sys.exit(1)
    file_path = sys.argv[1]

    sending_file = convert.convert(file_path)
    pico_util.send_file_to_pico('/dev/tty.usbmodem1101', sending_file)
    
