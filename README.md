# DAIN-Vulkan-GUI
AI-Powered video interpolater (eg. 30fps -> 60fps) for Vulkan devices. Based on dain-ncnn-vulkan and ffmpeg

WIP Software so expect bugs, GUI soon™

## Usage
Windows: `.\DAINVulkanCLI.exe -i "C:\Users\example\Videos\test.mp4" --output-folder "C:\Users\example\Videos\DainFolder"`

Linux: `./DAINVulkanCLI" -i "/home/example/Videos/test.mp4" --output-folder "/home/example/Videos/DainFolder"`

## Errors
"vkQueueSubmit failed" and "vkAllocateMemory failed" happens when there isn't enough VRAM for the current frame. Use a lower tile size or downscale the video. 

## Features
### What works
* Sequential frame handling (Removed frames affect video length)
* 2x, 3x, 4x, 5x, etc. Multiplier-target
* Multi-threading (-j)
* Multi-gpu (-g)

### Not implemented yet
* Timestamp frame handling (Video length preserved, times between frames accounted for)
* Perfect loop mode (Last frame leads into the first)
* Framerate-target

### Needs to be fixed by Dain-ncnn author
* Tiles don't overlap (artifacting when using tiles)
* Transparency (glitchy output currently)
* "vkWaitForFences failed" error when using large tilesizes on Windows

## Tips
The program can be set to process two frames at once (`-j 1:2:2`). This allows for the GPU to be used almost 100% of the time instead of pausing everytime a frame needs to be saved/loaded which gives a very slight speed increase. The downside however is that two frames will be in memory at once so a lower tile size will be needed if there isn't enough VRAM.  

Tiles are used by default which can slow down processing. Using a tilesize that's equal to or bigger then the video's resolution will disable tiles and process the frame all at once. Eg. 720p = 1280x720 so use `-t 1280`

## Help message
```
usage: DAINVulkanCLI.py [-h] -i INPUT_FILE [-o OUTPUT_FILE] [-O OUTPUT_FOLDER]
                        [-s FRAME_MULTIPLIER] [-fps TARGET_FPS]
                        [--interpolator INTERPOLATOR] [-g GPU_ID]
                        [-t TILESIZE] [-j THREAD_COUNT] [--steps STEPS]
                        [--input-fps INPUT_FPS] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        Path to input video
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Path to output final video to
  -O OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER
                        Folder to output work to
  -s FRAME_MULTIPLIER, --frame-multiplier FRAME_MULTIPLIER
                        Frame multiplier 2x,3x,etc (default=2)
  -fps TARGET_FPS, --target-fps TARGET_FPS
                        [Unimplemented] Calculates multiplier based on target
                        framerate
  --interpolator INTERPOLATOR
                        Pick interpolator: dain-ncnn, cain-ncnn (default=dain-
                        ncnn)
  -g GPU_ID, --gpu-id GPU_ID
                        GPU to use (default=auto) can be 0,1,2 for multi-gpu
  -t TILESIZE, --tilesize TILESIZE
                        Tile size (>=128, default=256) must be multiple of 32
                        ,can be 256,256,128 for multi-gpu
  -j THREAD_COUNT, --thread-count THREAD_COUNT
                        Thread count for load/process/save (default=1:2:2) can
                        be 1:2,2,2:2 for multi-gpu
  --steps STEPS         If specified only run certain steps 1,2,3 (eg. 1,2 for
                        1 & 2 only)
  --input-fps INPUT_FPS
                        Manually specify framerate of input video
  --verbose             Print additional info to the commandline
```

## Credits
https://github.com/nihui/dain-ncnn-vulkan Interpolation program that this project is a wrapper for

https://github.com/nihui/cain-ncnn-vulkan

https://ffmpeg.org/ All in one program for video decoding/encoding
