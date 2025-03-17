## Create new conda env
```
conda env create -f environment.yml
```

## Activate conda env
```
conda activate esp32
```

## Update environment
```
conda env update --file environment.yml --prune
```

## Remove conda env
```
conda remove --name <env> --all
```

## How to get serial port on Mac
```
ls /dev/cu.*
```

## Reset board firmware
### ESP32C6
```
esptool.py --chip esp32c6 --port /dev/tty.usbmodem1101 erase_flash
esptool.py --chip esp32c6 --port /dev/tty.usbmodem1101 write_flash -z 0 esp32c6-20241129-v1.24.1.bin
```
### ESP32S3
```
esptool.py --chip esp32c6 --port /dev/tty.usbmodem1101 erase_flash
esptool.py --chip esp32s3 --port /dev/tty.usbmodem1101 write_flash -z 0 ESP32_GENERIC_S3-20241129-v1.24.1.bin
```