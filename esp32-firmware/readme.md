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