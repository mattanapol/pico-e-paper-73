import urequests as requests
import json
import time
from machine import UART, Pin, deepsleep

DOWNLOADED_FILE_LIST = "/downloaded_files.txt"
UART_SEND_SLEEP_IN_SECONDS = 0.03
CHUNK_SIZE = 1024
DEEP_SLEEP_IN_SECONDS = 20

def read_config():
    with open("/config.json", "r") as f:
        config = json.load(f)
        return config

def connect_wifi(ssid, key):
    import network
    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, key)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ipconfig('addr4'))

def show_led(r, g, b):
    from neopixel import NeoPixel

    pin = Pin(8, Pin.OUT)
    np = NeoPixel(pin, 1)
    np[0] = (r, g, b)
    np.write()

def get_file_list(folder_id, google_api_key):
    folder_url = f"https://www.googleapis.com/drive/v3/files?q=\"{folder_id}\"+in+parents&fields=files(id,name,createdTime,size)&key={google_api_key}&orderBy=modifiedTime%20asc"
    response = requests.get(url=folder_url)
    if response.status_code != 200:
        print("Failed to get file list, Status code:", response.status_code)
        return []
    json_response = response.json()
    files = json_response["files"]
    for file in files:
        print(f"File ID: {file['id']}, Name: {file['name']}, Size: {file['size']}, Created Time: {file['createdTime']}")
    return files

def download_file(uart, google_api_key, file_id, file_name, file_size):
    download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={google_api_key}"
    print("Downloading file from:", download_url)
    print("File name:", file_name)
    print("File size:", file_size, "bytes")
    response = requests.get(download_url, stream=True)

    if response.status_code == 200:
        send_file_to_uart(uart, response.raw, file_name, file_size)
        print("File download and streaming completed successfully")
    else:
        print("Failed to download file, Status code:", response.status_code)

    response.close()

def send_file_to_uart(uart, stream, file_name, file_size):
    import struct
    file_path = f"pic/{file_name}"
    # Create the header
    header = struct.pack('256sI', file_path.encode('utf-8'), int(file_size))
    uart.write(header)
    while True:
        chunk = stream.read(CHUNK_SIZE)
        if not chunk:
            break
        uart.write(chunk)
        print("Chunk sent:", len(chunk), "bytes")
        time.sleep(UART_SEND_SLEEP_IN_SECONDS)

def compare_file_list(source_file_list, downloaded_file_list):
    downloaded_ids = {file['id'] for file in downloaded_file_list}
    downloaded = []
    missing = []

    for source_file in source_file_list:
        if source_file['id'] in downloaded_ids:
            for downloaded_file in downloaded_file_list:
                if source_file['id'] == downloaded_file['id']:
                    downloaded.append({
                        'id': source_file['id'],
                        'name': source_file['name'],
                        'size': source_file['size']
                    })
                    break
        else:
            missing.append(source_file)

    return downloaded, missing

def save_downloaded_files(downloaded_files):
    with open(DOWNLOADED_FILE_LIST, "w") as f:
        for file in downloaded_files:
            f.write(f"{file['id']},{file['name']}\n")

def append_downloaded_file(file_id, file_name):
    # Save the downloaded file id and file name to a file
    with open(DOWNLOADED_FILE_LIST, "a") as f:
        f.write(f"{file_id},{file_name}\n")

def load_downloaded_files():
    downloaded_files = []
    try:
        with open(DOWNLOADED_FILE_LIST, "r") as f:
            for line in f:
                file_id, file_name = line.strip().split(",")
                downloaded_files.append({"id": file_id, "name": file_name})
    except OSError:
        print("No downloaded file list found.")
    return downloaded_files
    
def init_uart():
    uart_tx = Pin(18, Pin.OUT)
    uart_rx = Pin(9, Pin.IN)
    uart = UART(1, baudrate=115200, tx=uart_tx, rx=uart_rx, timeout=1000, bits=8, parity=None, stop=1)
    return uart

show_led(0, 1, 0)
print("Reading config...")
config = read_config()
ssid=config["wifi_ssid"]
password=config["wifi_password"]
folder_id=config["folder_id"]
google_api_key=config["google_api_key"]

print("Connecting to wifi...")
connect_wifi(ssid, password)

print("Initializing UART...")
uart = init_uart()
print("Getting file list...")
files = get_file_list(folder_id, google_api_key)
show_led(1, 0, 0)
downloaded_files = load_downloaded_files()
downloaded_files, missing_files = compare_file_list(files, downloaded_files)
save_downloaded_files(downloaded_files)

for file in missing_files:
    download_file(uart, google_api_key, file["id"], file["name"], file["size"])
    append_downloaded_file(file["id"], file["name"])

print(f"All files downloaded successfully, going to deep sleep for {DEEP_SLEEP_IN_SECONDS} seconds.")
deepsleep(DEEP_SLEEP_IN_SECONDS * 1000)