AI-Powered video interpolater (eg. 30fps -> 60fps) for Vulkan devices. Based on dain-ncnn-vulkan and ffmpeg

WIP Software so expect bugs, GUI soon™

## Usage
Windows: `.\DAINVulkanCLI.exe -i "C:\Users\example\Videos\test.mp4" --output-folder "C:\Users\example\Videos\DainFolder"`

Linux: `./DAINVulkanCLI" -i "/home/example/Videos/test.mp4" --output-folder "/home/example/Videos/DainFolder"`

## Features
* Static frame interpolation
* Dynamic frame interpolation (duplicate frames are interpolated)
* Dain-ncnn: 2x, 3x, 4x, 5x, etc. Multiplier-target
* Cain-ncnn: 2x, 4x, 8x, etc. Multiplier-target
* Multi-threading (-j)
* Multi-gpu (-g)
* Automatic duplicate frame deletion
* Dynamic 1x mode (framerate stays the same, duplicate frames are replaced with interpolations)


## Credits
Interpolation programs that this project is a wrapper for:
* https://github.com/nihui/dain-ncnn-vulkan 
* https://github.com/nihui/cain-ncnn-vulkan

All in one program for video decoding/encoding:
* https://ffmpeg.org/ 
