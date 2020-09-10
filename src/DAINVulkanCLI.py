#!/usr/bin/env python3

import argparse
import pathlib
import tempfile
import subprocess
import sys
import os

programLocation = os.path.dirname(os.path.abspath(__file__))

# Default Global Variables
dainNcnnVulkanWindowsBinaryLocation = os.path.abspath(
    os.path.join(programLocation, "dependencies", "dain-ncnn-vulkan", "windows"))
dainNcnnVulkanLinuxBinaryLocation = os.path.abspath(
    os.path.join(programLocation, "dependencies", "dain-ncnn-vulkan", "ubuntu"))
dainGpuId = "auto"
dainThreads = "1:2:2"
dainTileSize = "256"

if sys.platform == "win32":
    dainNcnnVulkanBinaryLocation = dainNcnnVulkanWindowsBinaryLocation
    dainVulkanExec = os.path.join(".", "dain-ncnn-vulkan.exe")
else:
    dainNcnnVulkanBinaryLocation = dainNcnnVulkanLinuxBinaryLocation
    dainVulkanExec = os.path.join(".", "dain-ncnn-vulkan")


# DAIN Process Functions
def DainVulkanFileModeCommand(input0File, input1File, outputFile, timeStep):
    # Default to 0.5 if not specified
    if timeStep == None:
        timeStep = "0.5"
    subprocess.run([dainVulkanExec, "-0", os.path.abspath(input0File), "-1", os.path.abspath(input1File), "-o",
                    os.path.abspath(outputFile), "-s", timeStep, "-t", dainTileSize, "-g", dainGpuId, "-j",
                    dainThreads], cwd=dainNcnnVulkanBinaryLocation)


def DainVulkanFolderModeCommand(inputFolder, outputFolder, targetFrames):
    command = [dainVulkanExec, "-i", os.path.abspath(inputFolder), "-o", os.path.abspath(outputFolder), "-n",
               targetFrames, "-t", dainTileSize, "-g", dainGpuId, "-j", dainThreads]
    subprocess.run(command, cwd=dainNcnnVulkanBinaryLocation)


# FFMPEG Process Functions
def FfmpegExtractFrames(inputFile, outputFolder):  # "Step 1"
    # ffmpeg -i "$i" %06d.png
    command = ["ffmpeg", "-i", inputFile, os.path.join(outputFolder, "%10d.png")]
    subprocess.run(command)


def FfmpegEncodeFrames(inputFolder, outputFile, Framerate):
    # ffmpeg -framerate 48 -i interpolated_frames/%06d.png output.mp4
    command = ["ffmpeg", "-framerate", Framerate, "-i", os.path.join(inputFolder, "%06d.png"), outputFile]
    subprocess.run(command)


if __name__ == "__main__":
    # Console arguments
    parser = argparse.ArgumentParser()
    ## Path Arguments
    parser.add_argument("-i", "--input-file", help="Path to input video", action="store", required=True)
    parser.add_argument("-o", "--output-file", help="Path to output final video to", action="store")
    parser.add_argument("--output-folder", help="Folder to output work to", action="store",
                        default=(os.path.join(tempfile.gettempdir(), "DAIN-Vulkan-GUI")))
    ## Interpolation options
    parser.add_argument("-s", "--frame-multiplier", help="Frame multiplier 2x,3x,etc (default=2)", action="store",
                        type="float", default=2)
    parser.add_argument("-fps", "--target-fps", help="[Unimplemented]Calculates multiplier based on target framerate",
                        action="store")
    ## Dain-ncnn-vulkan pass-through options
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
        if os.path.exists(dainNcnnVulkanBinaryLocation):
            print("Using dain-ncnn-vulkan at", dainNcnnVulkanBinaryLocation)

    inputFile = os.path.abspath(args.input_file)
    outputFolder = os.path.abspath(args.output_folder)
    print("Input file:", inputFile)

    # Setup working folder
    dainWorkingFolder = os.path.join(outputFolder, pathlib.Path(inputFile).stem)
    pathlib.Path(dainWorkingFolder).mkdir(parents=True, exist_ok=True)
    print("Working Directory:", dainWorkingFolder)
    ## Setup original_frames folder
    dainOriginalFramesFolder = os.path.join(dainWorkingFolder, "original_frames")
    pathlib.Path(dainOriginalFramesFolder).mkdir(parents=True, exist_ok=True)
    ## Setup interpolated_frames folder
    dainInterpolatedFramesFolder = os.path.join(dainWorkingFolder, "interpolated_frames")
    pathlib.Path(dainInterpolatedFramesFolder).mkdir(parents=True, exist_ok=True)
    ## Setup output_videos folder
    dainOutputVideosFolder = os.path.join(dainWorkingFolder, "output_videos")
    pathlib.Path(dainOutputVideosFolder).mkdir(parents=True, exist_ok=True)

    if (stepsSelection is None) or ("1" in stepsSelection):
        print("Extracting frames to original_frames")
        FfmpegExtractFrames(inputFile, dainOriginalFramesFolder)

    print("Interpolation Multiplier:", args.frame_multiplier)
    ## Analyse original frames
    dainOriginalFramesArray = sorted(
        [f for f in os.listdir(dainOriginalFramesFolder) if os.path.isfile(os.path.join(dainOriginalFramesFolder, f))])
    dainOriginalFramesCount = len(dainOriginalFramesArray)
    print("Original frame count:", dainOriginalFramesCount)
    ## Calculate interpolated frames
    dainInterpolatedFramesCount = dainOriginalFramesCount * args.frame_multiplier
    print("Interpolated frame count", dainInterpolatedFramesCount)

    if (stepsSelection is None) or ("2" in stepsSelection):
        print("Processing frames to interpolated_frames")
        DainVulkanFolderModeCommand(dainOriginalFramesFolder, dainInterpolatedFramesFolder,
                                    str(dainInterpolatedFramesCount))

    if (stepsSelection is None) or ("1" in stepsSelection):
        print("Extracting frames to original_frames")
        FfmpegEncodeFrames(dainInterpolatedFramesFolder, dainOutputVideosFolder, "48")
