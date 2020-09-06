# DAIN-Vulkan-GUI

## Todo

Add windows support

Mode 3 & 4 support (timestamp modes)

Progress bar

## Usage
```
usage: DAINVulkanStep2.py [-h] [-s FRAMEMULTIPLIER] [--verbose] [-g GPUID] [-t TILESIZE]
                          [-j THREADCOUNT]
                          DainAppFolder

positional arguments:
  DainAppFolder

optional arguments:
  -h, --help            show this help message and exit
  -s FRAMEMULTIPLIER, --framemultiplier FRAMEMULTIPLIER
                        Frame multiplier 2x,3x,etc (default=2)
  --verbose             Print additional info to the commandline
  -g GPUID, --gpuid GPUID
                        GPU to use (default=auto) can be 0,1,2 for multi-gpu
  -t TILESIZE, --tilesize TILESIZE
                        Tile size (>=128, default=256) must be multiple of 32 ,can be 256,256,128
                        for multi-gpu
  -j THREADCOUNT, --threadcount THREADCOUNT
                        Thread count for load/process/save (default=1:2:2) can be 1:2,2,2:2 for
                        multi-gpu
```
