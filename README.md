# DAIN-Vulkan-GUI

DAINVulkanStep2: Uses frames extracted by DAIN-APP and interpolates them using Vulkan instead of CUDA

WIP Software so expect bugs
## Usage
Use DAIN-APP to extract a video using Step 1, find the folder it made that contains "config.json" and put the path of that folder in this program:

Windows: `.\DAINVulkanStep2.exe "C:\Users\default\Videos\DainAppFolder"`

Linux: `./DAINVulkanStep2 "/home/default/Video/DainAppFolder"`

For example, if you picked Interpolate 4x in DAIN-APP then use `-s 4` in this program. Scroll down to the Help page for more options

## Todo

* Mode 3 & 4 support

* Progress bar

* GUI

## Errors
"vkQueueSubmit failed" happens when there isn't enough VRAM for the current frame. Use a lower tile size

## Parity with DAIN-APP
### What works
* Mode 1 & 2 (Sequential modes)
* 2x, 3x, 4x, 5x, etc. Interpolation

### What doesn't work
* Mode 3 & 4 (Timestamp modes)
* Perfect loop

### Needs to be fixed by Dain-ncnn author
* Add Tile overlap (artifacting on motion when using tiles)
* Transparency (just causes glitchy output currently)

## Tips
By default the program will process two frames at once (`-j 1:2:2`). This allows for the GPU to be used almost 100% of the time instead of pausing everytime a frame needs to be saved/loaded. The downside of this is that two frames will be in memory at once so a lower tile size will be needed.
You can switch to one file at a time (like DAIN-APP) by using `-j 1:1:2` which will let you use a larger tilesize

Tiles are used by default which can slow down processing. Using a tilesize that's as big as the video's resolution will disable tiles and process the frame all at once. Eg. 720p = 1280x720 so use `-t 1280`

## Help page
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
