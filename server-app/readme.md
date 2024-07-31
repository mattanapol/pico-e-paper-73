## Create new conda env
```
conda env create -f environment.yml
```

## Activate conda env
```
conda activate pico-e-paper
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
ls -lha /dev/tty* > plugged.txt
ls -lha /dev/tty* > unplugged.txt
vimdiff plugged.txt unplugged.txt
```