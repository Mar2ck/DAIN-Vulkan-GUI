# DAIN-Vulkan-GUI
AI-Powered video interpolater (eg. 30fps -> 60fps) for Vulkan devices. Based on dain-ncnn-vulkan and ffmpeg

WIP Software so expect bugs, GUI soon™

## Usage
Windows: `.\DAINVulkanCLI.exe -i "C:\Users\example\Videos\test.mp4" --output-folder "C:\Users\example\Videos\DainAppFolder"`

Linux: `./DAINVulkanCLI" -i "/home/example/Videos/test.mp4" --output-folder "/home/example/Videos/DainAppFolder"`

## Errors
"vkQueueSubmit failed" and "vkAllocateMemory failed" happens when there isn't enough VRAM for the current frame. Use a lower tile size or downscale the video. 

## Features
### What works
* Sequential frame handling (Removed frames affect video length)
* 2x, 3x, 4x, 5x, etc. Multiplier-target

### Not implemented yet
* Timestamp frame handling (Video length preserved, times between frames accounted for)
* Perfect loop mode (Last frame leads into the first)
* Framerate-target

### Needs to be fixed by Dain-ncnn author
* Tiles don't overlap (artifacting when using tiles)
* Transparency (glitchy output currently)

## Tips
By default the program will process two frames at once (`-j 1:2:2`). This allows for the GPU to be used almost 100% of the time instead of pausing everytime a frame needs to be saved/loaded. The downside of this is that two frames will be in memory at once so a lower tile size will be needed if there isn't enough VRAM. You can switch to one file at a time (like DAIN-APP) by using `-j 1:1:1` which will let you use a larger tilesize/no tiles. 

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

## Credits
https://github.com/nihui/dain-ncnn-vulkan Interpolation program that this project is a wrapper for

https://ffmpeg.org/ All in one program for video decoding/encoding
