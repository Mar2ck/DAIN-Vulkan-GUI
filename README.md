# DAIN-Vulkan-GUI

## Todo

Add windows support

Mode 3 & 4 support (timestamp modes)

Progress bar

## Errors
"vkQueueSubmit failed" happens when there isn't enough VRAM for the current frame. Use a lower tile size

## Tips
By default the program will process two frames at once (`-j 1:2:2`). This allows for the GPU to be used almost 100% of the time instead of pausing everytime a frame needs to be saved/loaded. The downside of this is that two frames will be in memory at once so a lower tile size will be needed.
You can switch to one file at a time (like DAIN-APP) by using `-j 1:1:2` which will let you use a larger tilesize

Tiles are used by default which can slow down processing. Using a tilesize larger then the video's resolution eg. `-t 4096` will disable tiles and process the video all at once

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
