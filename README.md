# DAIN-Vulkan-GUI
AI-Powered video interpolater (eg. 30fps -> 60fps) for Vulkan devices. Based on dain-ncnn-vulkan and ffmpeg

WIP Software so expect bugs, GUI soon™

## Download
Windows | Linux | Google Colab
:-: | :-: | :-:
[![windows](./res/windows-64x.png "Windows")](https://github.com/Mar2ck/DAIN-Vulkan-GUI/releases) | [![linux](./res/linux-64x.png "Linux")](https://github.com/Mar2ck/DAIN-Vulkan-GUI/releases) | [![colab](./res/colab-64x.png "Google Colab")](https://colab.research.google.com/github/Mar2ck/DAIN-Vulkan-GUI/blob/master/DAINVulkanCLI-Colab.ipynb)


## Usage
Windows: `.\DAINVulkanCLI.exe -i "C:\Users\example\Videos\test.mp4" --output-folder "C:\Users\example\Videos\DainFolder"`

Linux: `./DAINVulkanCLI -i "/home/example/Videos/test.mp4" --output-folder "/home/example/Videos/DainFolder"`

## Features
* Static frame interpolation
* Dain-ncnn: 2x, 3x, 4x, 5x, etc. Multiplier-target
* Cain-ncnn, Rife-ncnn: 2x, 4x, 8x, etc. Multiplier-target
* Multi-threading (-j)
* Multi-gpu (-g)
* Dynamic interpolation (dain-ncnn) (duplicate frames are interpolated)
* Dynamic 1x mode (framerate stays the same, duplicate frames are replaced with interpolations)

### Todo
* Dynamic interpolation (cain-ncnn, RIFE)
* Perfect loop (Last frame leads into the first)
* Framerate-target
* Slow-mo mode (framerate stays the same, video is slowed down via interpolation)

### Needs to be fixed by Dain-ncnn author
* Tiles don't overlap (artifacting when using tiles)
* Transparency (glitchy output currently)
* "vkWaitForFences failed" error when using large tilesizes on Windows

## Tips
The program can be set to process two frames at once (`-j 1:2:2`). This allows for the GPU to be used almost 100% of the time instead of pausing everytime a frame needs to be saved/loaded which gives a very slight speed increase. The downside however is that two frames will be in memory at once so a lower tile size will be needed if there isn't enough VRAM.  

Tiles are used by default which can slow down processing. Using a tilesize that's equal to or bigger then the video's resolution will disable tiles and process the frame all at once. Eg. 720p = 1280x720 so use `-t 1280`

## Errors
"vkQueueSubmit failed" and "vkAllocateMemory failed" happens when there isn't enough VRAM for the current frame. Use a lower tile size or downscale the video. 

## Help message
```
usage: DAINVulkanCLI.py [-h] -i INPUT_FILE -O OUTPUT_FOLDER [-o OUTPUT_FILE]
                        [--delete-output-folder] [-m INTERPOLATION_MODE]
                        [-x FRAME_MULTIPLIER] [--target-fps TARGET_FPS]
                        [-e INTERPOLATOR_ENGINE] [--loop-video]
                        [--duplicate-auto-delete DUPLICATE_AUTO_DELETE]
                        [-g GPU_ID] [-t TILE_SIZE] [-j THREADS]
                        [--steps STEPS] [--video-type VIDEO_TYPE]
                        [--copy-mtime] [--input-fps INPUT_FPS] [--verbose]
                        [--debug]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        Path to input video
  -O OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER
                        Folder to output work to
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Path to copy final video to (can be directory or file
                        path)
  --delete-output-folder
                        Delete output folder at the end, intended to be used
                        with --output-file
  -m INTERPOLATION_MODE, --interpolation-mode INTERPOLATION_MODE
                        Interpolation type (static/dynamic, default=static)
  -x FRAME_MULTIPLIER, --frame-multiplier FRAME_MULTIPLIER
                        Frame multiplier 2x,3x,etc (default=2)
  --target-fps TARGET_FPS
                        Calculates frame multiplier based on a target
                        framerate
  -e INTERPOLATOR_ENGINE, --interpolator-engine INTERPOLATOR_ENGINE
                        Pick interpolator: dain-ncnn, cain-ncnn, rife-ncnn
                        (default=dain-ncnn)
  --loop-video          [Unimplemented] Interpolates video as a loop (last
                        frame leads into the first)
  --duplicate-auto-delete DUPLICATE_AUTO_DELETE
                        Based on a percentage (Eg. 0.95) will delete any
                        frames found to be more similar
  -g GPU_ID, --gpu-id GPU_ID
                        GPU to use (default=auto) can be 0,1,2 for multi-gpu
  -t TILE_SIZE, --tile-size TILE_SIZE
                        Tile size (>=128, default=256) must be multiple of 32,
                        can be 256,256,128 for multi-gpu
  -j THREADS, --threads THREADS
                        Thread count for load/process/save (default=1:2:2) can
                        be 1:2,2,2:2 for multi-gpu
  --steps STEPS         If specified only run certain steps 1,2,3 (eg. 1,2 for
                        1 & 2 only)
  --video-type VIDEO_TYPE
                        Video type for output video eg. mp4, webm, mkv
                        (default=mp4)
  --copy-mtime          Copy the modified timestamp to output
  --input-fps INPUT_FPS
                        Manually specify framerate of input video
  --verbose             Print additional info to the commandline
  --debug               Print debug messages to the commandline
```

## Credits
Interpolation programs that this project is a wrapper for:
* https://github.com/nihui/dain-ncnn-vulkan 
* https://github.com/nihui/cain-ncnn-vulkan
* https://github.com/nihui/rife-ncnn-vulkan
* https://github.com/hzwer/arXiv2020-RIFE

All in one program for video decoding/encoding:
* https://ffmpeg.org/ 
