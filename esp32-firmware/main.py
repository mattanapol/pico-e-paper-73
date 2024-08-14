import time
import wifi
import json
import alarm
import socketpool
import adafruit_requests as requests
import ssl
import board
import neopixel
import busio

DOWNLOADED_FILE_LIST = "/downloaded_files.txt"

def read_config():
    with open("/config.json", "r") as f:
        config = json.load(f)
        return config
    
def deep_sleep(seconds):
    print(f"Going to deep sleep for {seconds} seconds...")
    # Calculate the wake-up time in monotonic time
    wake_up_time = time.monotonic() + seconds
    time_alarm = alarm.time.TimeAlarm(monotonic_time=wake_up_time)

    # Enter deep sleep until the alarm triggers
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)

def get_file_list(request, folder_id, google_api_key):
    folder_url = f"https://www.googleapis.com/drive/v3/files?q=\"{folder_id}\"+in+parents&fields=files(id,name,createdTime,size)&key={google_api_key}&orderBy=modifiedTime asc"
    response = request.get(folder_url)
    if response.status_code != 200:
        print("Failed to get file list, Status code:", response.status_code)
        return []
    json_response = response.json()
    files = json_response.get("files", [])
    for file in files:
        print(f"File ID: {file['id']}, Name: {file['name']}, Created Time: {file['createdTime']}")
    return files

def download_file(request, uart, file_id, google_api_key):
    download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={google_api_key}"
    print("Downloading file from:", download_url)
    response = request.get(download_url, stream=True)
    chunk_size = 1024  # Download in 1KB chunks

    if response.status_code == 200:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                uart.write(chunk)
                print("Chunk sent:", len(chunk), "bytes")
                time.sleep(0.03)  # Small delay to ensure smooth transmission
        print("File download and streaming completed successfully")
    else:
        print("Failed to download file, Status code:", response.status_code)

    response.close()

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
    

def main_task():
    pixel.fill((0, 255, 0))
    print("Starting main task.")

    pool = socketpool.SocketPool(wifi.radio)
    request = requests.Session(pool, ssl.create_default_context())
    uart = busio.UART(board.IO5, board.IO4, baudrate=115200)
    files = get_file_list(request, config["folder_id"], config["google_api_key"])
    downloaded_files = load_downloaded_files()
    downloaded_files, missing_files = compare_file_list(files, downloaded_files)
    save_downloaded_files(downloaded_files)

    for file in missing_files:
        download_file(request, uart, file["id"], config["google_api_key"])
        append_downloaded_file(file["id"], file["name"])

uart = busio.UART(tx=board.TX, rx=board.RX, baudrate=115200)
uart.write(b"Hello from ESP32!\n")
print("Reading config...")
config = read_config()
ssid=config["wifi_ssid"]
password=config["wifi_password"]
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.01)

print("Connecting to wifi...")
pixel.fill((255, 0, 0))
if not wifi.radio.connect(ssid=ssid,password=password): # return None if success
    print("connected to wifi!")
    print("my IP addr:", wifi.radio.ipv4_address)
    main_task()

pixel.fill((0, 0, 0))
deep_sleep(10)


