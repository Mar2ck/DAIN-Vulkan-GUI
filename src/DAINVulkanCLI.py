#!/usr/bin/env python3

import argparse
import json
import pathlib
import tempfile
import subprocess
import sys
import os

programLocation = os.path.dirname(os.path.abspath(__file__))

# Dain-ncnn Location
dainNcnnVulkanWindowsBinaryLocation = os.path.join(
    programLocation, "dependencies", "dain-ncnn-vulkan", "windows")
dainNcnnVulkanLinuxBinaryLocation = os.path.join(
    programLocation, "dependencies", "dain-ncnn-vulkan", "ubuntu")

# Cain-ncnn Location
cainNcnnVulkanWindowsBinaryLocation = os.path.join(
    programLocation, "dependencies", "cain-ncnn-vulkan", "windows")
cainNcnnVulkanLinuxBinaryLocation = os.path.join(
    programLocation, "dependencies", "cain-ncnn-vulkan", "ubuntu")

# Interpolation Defaults
dainGpuId = "auto"
dainThreads = "1:1:1"
dainTileSize = "256"

if sys.platform == "win32":
    # Windows
    dainNcnnVulkanBinaryLocation = dainNcnnVulkanWindowsBinaryLocation
    dainVulkanExec = os.path.join(dainNcnnVulkanWindowsBinaryLocation, "dain-ncnn-vulkan.exe")

    cainNcnnVulkanBinaryLocation = cainNcnnVulkanWindowsBinaryLocation
    cainVulkanExec = os.path.join(cainNcnnVulkanWindowsBinaryLocation, "cain-ncnn-vulkan.exe")
else:
    # Linux
    dainNcnnVulkanBinaryLocation = dainNcnnVulkanLinuxBinaryLocation
    dainVulkanExec = os.path.join(dainNcnnVulkanLinuxBinaryLocation, "dain-ncnn-vulkan")

    cainNcnnVulkanBinaryLocation = cainNcnnVulkanLinuxBinaryLocation
    cainVulkanExec = os.path.join(cainNcnnVulkanLinuxBinaryLocation, "cain-ncnn-vulkan")

# Dain-ncnn Interpolation Functions
def DainVulkanFileModeCommand(input0File, input1File, outputFile, timeStep):
    # Default to 0.5 if not specified
    if timeStep == None:
        timeStep = "0.5"
    pathlib.Path(os.path.dirname(outputFile)).mkdir(parents=True, exist_ok=True)  # Create parent folder of outputFile
    command = [dainVulkanExec, "-0", os.path.abspath(input0File), "-1", os.path.abspath(input1File), "-o",
               os.path.abspath(outputFile), "-s", timeStep, "-t", dainTileSize, "-g", dainGpuId, "-j", dainThreads]
    subprocess.run(command, cwd=dainNcnnVulkanBinaryLocation)

def DainVulkanFolderModeCommand(inputFolder, outputFolder, targetFrames):
    pathlib.Path(outputFolder).mkdir(parents=True, exist_ok=True)  # Create outputFolder
    command = [dainVulkanExec, "-i", os.path.abspath(inputFolder), "-o", os.path.abspath(outputFolder), "-n",
               targetFrames, "-t", dainTileSize, "-g", dainGpuId, "-j", dainThreads]
    subprocess.run(command, cwd=dainNcnnVulkanBinaryLocation)

# Cain-ncnn Interpolation Functions
def CainVulkanFileModeCommand(input0File, input1File, outputFile): # Doesn't support timestep
    pathlib.Path(os.path.dirname(outputFile)).mkdir(parents=True, exist_ok=True)  # Create parent folder of outputFile
    command = [cainVulkanExec, "-0", os.path.abspath(input0File), "-1", os.path.abspath(input1File), "-o",
               os.path.abspath(outputFile), "-t", dainTileSize, "-g", dainGpuId, "-j", dainThreads]
    subprocess.run(command, cwd=cainNcnnVulkanBinaryLocation)

def CainVulkanFolderModeCommand(inputFolder, outputFolder): # Output frames are always double of input
    pathlib.Path(outputFolder).mkdir(parents=True, exist_ok=True)  # Create outputFolder
    command = [cainVulkanExec, "-i", os.path.abspath(inputFolder), "-o", os.path.abspath(outputFolder),
               "-t", dainTileSize, "-g", dainGpuId, "-j", dainThreads]
    subprocess.run(command, cwd=cainNcnnVulkanBinaryLocation)

# FFmpeg Process Functions
def FfmpegExtractFrames(inputFile, outputFolder):  # "Step 1"
    # ffmpeg -i "$i" %06d.png
    pathlib.Path(outputFolder).mkdir(parents=True, exist_ok=True) # Create outputFolder
    command = ["ffmpeg", "-i", inputFile, "-loglevel", "error", os.path.join(outputFolder, "%06d.png")]
    subprocess.run(command)

def FfmpegEncodeFrames(inputFolder, outputFile, Framerate):
    # ffmpeg -framerate 48 -i interpolated_frames/%06d.png output.mp4
    pathlib.Path(os.path.dirname(outputFile)).mkdir(parents=True, exist_ok=True) # Create parent folder of outputFile
    command = ["ffmpeg", "-framerate", Framerate, "-i", os.path.join(inputFolder, "%06d.png"), "-crf", "18", "-y",
               "-loglevel", "error", outputFile]
    subprocess.run(command)

#FFprobe Process Functions
def FfprobeCollectVideoInfo(inputFile):
    # ffprobe -show_streams -print_format json -loglevel quiet input.mp4
    # Some videos don't return "duration" such as webm, apng
    command = ["ffprobe", "-show_streams", "-print_format", "json", "-loglevel", "quiet", inputFile]
    output = subprocess.check_output(command, universal_newlines=True)
    parsedOutput = json.loads(output)["streams"][0]
    return({
        "width": parsedOutput["width"],
        "height": parsedOutput["height"],
        "fps": parsedOutput["r_frame_rate"],
        "fpsAverage": parsedOutput["avg_frame_rate"]
    })

def FfprobeCollectFrameInfo(inputFile): # Will be needed for a timestamp mode
    # ffprobe -show_frames -print_format json -loglevel quiet input.mp4
    pass

if __name__ == "__main__":
    # Console arguments
    parser = argparse.ArgumentParser()
    ## Path Arguments
    parser.add_argument("-i", "--input-file", help="Path to input video", action="store", required=True)
    parser.add_argument("-o", "--output-file", help="Path to output final video to", action="store")
    parser.add_argument("-O", "--output-folder", help="Folder to output work to", action="store",
                        default=(os.path.join(tempfile.gettempdir(), "DAIN-Vulkan-GUI")))
    ## Interpolation options
    parser.add_argument("-s", "--frame-multiplier", help="Frame multiplier 2x,3x,etc (default=2)", action="store",
                        type=float, default=2)
    parser.add_argument("-fps", "--target-fps", help="[Unimplemented] Calculates multiplier based on target framerate",
                        action="store")
    parser.add_argument("--interpolator", help="Pick interpolator: dain-ncnn, cain-ncnn (default=dain-ncnn)",
                        action="store", default="dain-ncnn")
    ## Dain-ncnn/Cain-ncnn pass-through options
    parser.add_argument("-g", "--gpu-id", help="GPU to use (default=auto) can be 0,1,2 for multi-gpu", action="store")
    parser.add_argument("-t", "--tilesize",
                        help="Tile size (>=128, default=256) must be multiple of 32 ,can be 256,256,128 for multi-gpu",
                        action="store")
    parser.add_argument("-j", "--thread-count",
                        help="Thread count for load/process/save (default=1:2:2) can be 1:2,2,2:2 for multi-gpu",
                        action="store")
    ## Step arguments
    parser.add_argument("--steps", help="If specified only run certain steps 1,2,3 (eg. 1,2 for 1 & 2 only)",
                        action="store")
    ## Debug options
    parser.add_argument("--input-fps", help="Manually specify framerate of input video", action="store")
    parser.add_argument("--verbose", help="Print additional info to the commandline", action="store_true")
    args = parser.parse_args()

    # Override global variables with arguments
    if args.gpu_id is not None:
        dainGpuId = args.gpu_id
    if args.thread_count is not None:
        dainThreads = args.thread_count
    if args.tilesize is not None:
        dainTileSize = args.tilesize

    if args.steps is None:
        stepsSelection = None
    else:
        stepsSelection = args.steps.split(",")

    print("GPU Selection:", dainGpuId)
    print("Threads:", dainThreads)
    print("Tilesize:", dainTileSize)
    if args.verbose is True:
        print("Platform:", sys.platform)

    inputFile = os.path.abspath(args.input_file)
    outputFolder = os.path.abspath(args.output_folder)
    print("Input file:", inputFile)

    inputFileProperties = FfprobeCollectVideoInfo(inputFile)
    if args.input_fps is not None:
        inputFileFps = args.input_fps
    else:
        fracNum, fracDenom = inputFileProperties["fpsAverage"].split("/")
        inputFileFps = int(fracNum) / int(fracDenom)

    # Setup working folder
    folderBase = os.path.join(outputFolder, pathlib.Path(inputFile).stem)
    print("Working Directory:", folderBase)
    ## Setup original_frames folder
    folderOriginalFrames = os.path.join(folderBase, "original_frames")
    ## Setup interpolated_frames folder
    folderInterpolatedFrames = os.path.join(folderBase, "interpolated_frames")
    ## Setup output_videos folder
    folderOutputVideos = os.path.join(folderBase, "output_videos")

    if (stepsSelection is None) or ("1" in stepsSelection):
        print("Step 1: Extracting frames to original_frames")
        FfmpegExtractFrames(inputFile, folderOriginalFrames)

    ## Analyse original frames
    folderOriginalFramesArray = sorted(os.listdir(folderOriginalFrames))
    folderOriginalFramesCount = len(folderOriginalFramesArray)
    print("Original frame count:", folderOriginalFramesCount)
    ## Calculate interpolated frames
    folderInterpolatedFramesCount = folderOriginalFramesCount * args.frame_multiplier
    print("Interpolated frame count", folderInterpolatedFramesCount)

    if (stepsSelection is None) or ("2" in stepsSelection):
        print("Step 2: Processing frames to interpolated_frames using", args.interpolator)
        if args.interpolator == "dain-ncnn":
            print("Interpolation Multiplier:", args.frame_multiplier)
            DainVulkanFolderModeCommand(folderOriginalFrames,
                                        folderInterpolatedFrames,
                                        str(folderInterpolatedFramesCount))
        elif args.interpolator == "cain-ncnn":
            CainVulkanFolderModeCommand(folderOriginalFrames,
                                        folderInterpolatedFrames)
        else:
            print("Invalid interpolator option")
            exit(1)

    if (stepsSelection is None) or ("3" in stepsSelection):
        print("Step 3: Extracting frames to output_videos")
        FfmpegEncodeFrames(folderInterpolatedFrames, os.path.join(folderOutputVideos, "output.mp4"), str(inputFileFps * args.frame_multiplier))
