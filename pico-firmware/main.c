#include "EPD_Test.h"   // Examples
#include "run_File.h"
#include "f_util.h"

#include "led.h"
#include "waveshare_PCF85063.h" // RTC
#include "DEV_Config.h"

#include <time.h>

#include "pico/stdlib.h"
#include "tusb.h"
#include "utils.h"

extern const char *fileList;
extern char pathName[];

void run_display(Time_data Time, Time_data alarmTime, char hasCard);
float measureVBAT(void);
void stopProcessingFile(void);
void startReceiveFile(void);
void on_receive_complete(void);

#define enChargingRtc 0

/*
Mode 0: Automatically get pic folder names and sort them
Mode 1: Automatically get pic folder names but not sorted
Mode 2: pic folder name is not automatically obtained, users need to create fileList.txt file and write the picture name in TF card by themselves
*/
#define Mode 1

#define BUFFER_SIZE 256
char buffer[BUFFER_SIZE];

// const char *pic_dir = "pic/";
// char file_path[256] = "";
bool processing_file = false;
int idle_counter = 0;
bool done_flag = false;

// Ring buffer size
#define RING_BUFFER_SIZE 40960 // 40KB
#define WRITE_BUFFER_SIZE 4096
uint8_t data[WRITE_BUFFER_SIZE];

#define HEADER_SIZE 260 // 256 bytes for filename + 4 bytes for size
uint8_t header_buffer[HEADER_SIZE];
uint32_t header_bytes_received = 0;


// Ring buffer structure
typedef struct {
    uint8_t buffer[RING_BUFFER_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
} ring_buffer_t;

// File information structure
typedef struct {
    char file_name[256];
    uint32_t file_size;
} file_info_t;

// Global file info
file_info_t received_file_info;
bool header_received = false;

uint32_t written_bytes = 0;
uint32_t bytes_received = 0;
uint32_t last_bytes_received = 0;

// Initialize the ring buffer
ring_buffer_t usb_rx_ring_buffer = { .head = 0, .tail = 0 };

// Function to add data to the ring buffer
bool ring_buffer_write(ring_buffer_t *rb, const uint8_t *data, uint32_t length) {
    for (uint32_t i = 0; i < length; i++) {
        uint32_t next = (rb->head + 1) % RING_BUFFER_SIZE;
        if (next == rb->tail) {
            // Buffer is full, data will be lost
            printf("Buffer overflow. Data lost.\n");
            return false;
        }
        rb->buffer[rb->head] = data[i];
        rb->head = next;
    }
    return true;
}

// Function to read data from the ring buffer
uint32_t ring_buffer_read(ring_buffer_t *rb, uint8_t *data, uint32_t length) {
    uint32_t count = 0;
    while (count < length && rb->tail != rb->head) {
        data[count++] = rb->buffer[rb->tail];
        rb->tail = (rb->tail + 1) % RING_BUFFER_SIZE;
    }
    return count;
}

void write_buffer_to_file(uint8_t *buffer, uint32_t size, bool append) {
    // Mount SD card (if not already mounted)
    run_mount();

    BYTE mode;
    if (append) {
        mode = FA_OPEN_APPEND | FA_WRITE;
    } else {
        mode = FA_CREATE_ALWAYS | FA_WRITE;
    }

    // Open file for appending
    FIL fil;
    FRESULT fr = f_open(&fil, received_file_info.file_name, mode);
    if (FR_OK != fr && FR_EXIST != fr) {
        printf("f_open error: %s (%d)\n", FRESULT_str(fr), fr);
        // Handle error
        return;
    }

    // Write buffer to file
    UINT bw;
    fr = f_write(&fil, buffer, size, &bw);
    if (fr != FR_OK) {
        printf("f_write error: %s (%d)\n", FRESULT_str(fr), fr);
        // Handle error
        return;
    }

    // Close file
    fr = f_close(&fil);
    if (FR_OK != fr) {
        printf("f_close error: %s (%d)\n", FRESULT_str(fr), fr);
        // Handle error
        return;
    }

    run_unmount();
    written_bytes += size;
    // printf("Received %d, Written: %d\n", bytes_received, written_bytes);
}

// Function to handle USB data reception
void tud_cdc_rx_cb(uint8_t itf) {

    // Read received data
    uint32_t count = tud_cdc_n_read(itf, buffer, BUFFER_SIZE);

    if (count) {
        startReceiveFile();
        bytes_received += count;
        ring_buffer_write(&usb_rx_ring_buffer, buffer, count);
    }
}

// Function to process the header
bool process_header() {
    // Calculate how many bytes to read
    uint32_t bytes_to_read = HEADER_SIZE - header_bytes_received;
    uint32_t count = ring_buffer_read(&usb_rx_ring_buffer, header_buffer + header_bytes_received, bytes_to_read);
    header_bytes_received += count;

    if (header_bytes_received < HEADER_SIZE) {
        printf("Header bytes received: %d\n", header_bytes_received);
        return false; // Not enough data for header yet
    }

    // Extract file name
    memset(received_file_info.file_name, 0, 256);
    memcpy(received_file_info.file_name, header_buffer, 256);
    received_file_info.file_name[255] = '\0'; // Ensure null-termination

    // Extract file size
    received_file_info.file_size = *(uint32_t*)(header_buffer + 256);

    header_received = true;
    memset(header_buffer, 0, HEADER_SIZE);
    header_bytes_received = 0;
    printf("Received Header - File: %s, Size: %u bytes\n", received_file_info.file_name, received_file_info.file_size);
    return true;
}

// Function to process the received data
void process_data() {
    int buffer_counter = 0;
    while (true) {
        uint32_t count = ring_buffer_read(&usb_rx_ring_buffer, data, WRITE_BUFFER_SIZE);
        if (count == 0) {
            break;
        }
        if(!sdTest()) 
        {
            write_buffer_to_file(data, count, written_bytes > 0);
        }
        buffer_counter++;
    }
    printf("Buffer counter: %d\n", buffer_counter);
    if (written_bytes >= received_file_info.file_size) {
        on_receive_complete();
    } else {
        printf("Waiting for more data..., written: %d/%d\n", written_bytes, received_file_info.file_size);
    }
}

void on_receive_complete() {
    stopProcessingFile();
    printf("File received: %s\n", received_file_info.file_name);
    if (is_str_end_with(received_file_info.file_name, ".bmp")) {
        sdScanDir();
        setPathIndexToLast();
    }
    else if (is_str_end_with(received_file_info.file_name, "keepList.txt")) {
        delete_files_not_in_list(received_file_info.file_name, picDir);
        sdScanDir();
        setPathIndexToLast();
    }

    done_flag = true;
}

void stopProcessingFile() {
    if (processing_file) {
        gpio_put(LED_ACT, 0);
        processing_file = false;
        header_received = false;
        bytes_received = 0;
        written_bytes = 0;
        idle_counter = 0;
        last_bytes_received = 0;
        memset(usb_rx_ring_buffer.buffer, 0, RING_BUFFER_SIZE);
        printf("Stop processing file\n");
    }
}

void startReceiveFile() {
    if (!processing_file) {
        gpio_put(LED_ACT, 1);
        processing_file = true;
        header_received = false;
        bytes_received = 0;
        written_bytes = 0;
        idle_counter = 0;
        printf("Start receiving file\n");
    }
}

float measureVBAT(void)
{
    float Voltage=0.0;
    const float conversion_factor = 3.3f / (1 << 12);
    uint16_t result = adc_read();
    Voltage = result * conversion_factor * 3;
    // printf("Raw value: 0x%03x, voltage: %f V\n", result, Voltage);
    return Voltage;
}

void chargeState_callback() 
{
    if(DEV_Digital_Read(VBUS)) {
        if(!DEV_Digital_Read(CHARGE_STATE)) {  // is charging
            ledCharging();
        }
        else {  // charge complete
            ledCharged();
        }
    }
}

void run_display(Time_data Time, Time_data alarmTime, char hasCard)
{
    if(hasCard) {
        setFilePath();
        EPD_7in3f_display_BMP(pathName, measureVBAT());   // display bmp
    }
    else {
        EPD_7in3f_display(measureVBAT());
    }

    PCF85063_clear_alarm_flag();    // clear RTC alarm flag
    rtcRunAlarm(Time, alarmTime);  // RTC run alarm
}

int main(void)
{
    Time_data Time = {2024-2000, 3, 31, 0, 0, 0};
    Time_data alarmTime = Time;
    // alarmTime.seconds += 10;
    // alarmTime.minutes += 30;
    alarmTime.hours +=24;
    char isCard = 0;
  
    printf("Init...\r\n");
    if(DEV_Module_Init() != 0) {  // DEV init
        return -1;
    }
    
    watchdog_enable(8*1000, 1);    // 8s
    DEV_Delay_ms(1000);
    PCF85063_init();    // RTC init
    rtcRunAlarm(Time, alarmTime);  // RTC run alarm
    gpio_set_irq_enabled_with_callback(CHARGE_STATE, GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL, true, chargeState_callback);

    if(measureVBAT() < 3.1) {   // battery power is low
        printf("low power ...\r\n");
        PCF85063_alarm_Time_Disable();
        ledLowPower();  // LED flash for Low power
        powerOff(); // BAT off
        return 0;
    }
    else {
        printf("work ...\r\n");
        ledPowerOn();
    }

    if(!sdTest()) 
    {
        isCard = 1;
        if(Mode == 0)
        {
            sdScanDir();
            file_sort();
        }
        if(Mode == 1)
        {
            sdScanDir();
        }
        if(Mode == 2)
        {
            file_cat();
        }
        
    }
    else 
    {
        isCard = 0;
    }

    if(!DEV_Digital_Read(VBUS)) {    // no charge state
        run_display(Time, alarmTime, isCard);
    }
    else {  // charge state
        // stdio_init_all();
        gpio_init(LED_ACT);
        gpio_set_dir(LED_ACT, GPIO_OUT);

        tusb_init();

        chargeState_callback();
        while(DEV_Digital_Read(VBUS)) {
            measureVBAT();

            tud_task();
            if (processing_file && !header_received) {
                process_header();
            } else if (processing_file && header_received) {
                process_data();
            }
            if (bytes_received > 0 && bytes_received == last_bytes_received) {
                idle_counter++;
                if (idle_counter > 10) {
                    stopProcessingFile();
                }
            }
            last_bytes_received = bytes_received;

            if(!DEV_Digital_Read(BAT_STATE) || (done_flag && !processing_file)) {  // KEY pressed
                printf("key interrupt\r\n");
                run_display(Time, alarmTime, isCard);
                done_flag = false;
            }
            DEV_Delay_ms(200);
        }
    }
    
    printf("power off ...\r\n");
    powerOff(); // BAT off

    return 0;
}
