#!/usr/bin/env python3
"""
This file is the core of DAIN-Vulkan-GUI and it's CLI interface
"""
#Built-in modules
import argparse
import json
import os
import pathlib
from platform import system
from shutil import which
import subprocess

programLocation = os.path.dirname(os.path.abspath(__file__))

# Dain-ncnn-vulkan binary location
dainNcnnExec = {}
dainNcnnExec["Windows"] = os.path.join(programLocation, "dependencies", "dain-ncnn-vulkan", "dain-ncnn-vulkan.exe")
dainNcnnExec["Darwin"] = os.path.join(programLocation, "dependencies", "dain-ncnn-vulkan", "dain-ncnn-vulkan-macos")
dainNcnnExec["Linux"] = os.path.join(programLocation, "dependencies", "dain-ncnn-vulkan", "dain-ncnn-vulkan-ubuntu")
dainNcnnExecDirectory = pathlib.Path(dainNcnnExec[system()]).parent
# Cain-ncnn-vulkan binary location
cainNcnnExec = {}
cainNcnnExec["Windows"] = os.path.join(programLocation, "dependencies", "cain-ncnn-vulkan", "cain-ncnn-vulkan.exe")
cainNcnnExec["Darwin"] = os.path.join(programLocation, "dependencies", "cain-ncnn-vulkan", "cain-ncnn-vulkan-macos")
cainNcnnExec["Linux"] = os.path.join(programLocation, "dependencies", "cain-ncnn-vulkan", "cain-ncnn-vulkan-ubuntu")
cainNcnnExecDirectory = pathlib.Path(cainNcnnExec[system()]).parent

# FFmpeg binary location
ffmpegExec = {}
ffmpegExec["Windows"] = os.path.join(programLocation, "dependencies", "ffmpeg", "windows", "ffmpeg.exe")
ffmpegExec["Darwin"] = os.path.join(programLocation, "dependencies", "ffmpeg", "macos", "ffmpeg")
ffmpegExec["Linux"] = os.path.join(programLocation, "dependencies", "ffmpeg", "linux", "ffmpeg")
if os.path.isfile(ffmpegExec[system()]) is False:
    ffmpegExec[system()] = which("ffmpeg") # Use the system version if bundled version not found
# FFprobe binary location
ffprobeExec = {}
ffprobeExec["Windows"] = os.path.join(programLocation, "dependencies", "ffmpeg", "windows", "ffprobe.exe")
ffprobeExec["Darwin"] = os.path.join(programLocation, "dependencies", "ffmpeg", "macos", "ffprobe")
ffprobeExec["Linux"] = os.path.join(programLocation, "dependencies", "ffmpeg", "linux", "ffprobe")
if os.path.isfile(ffprobeExec[system()]) is False:
    ffprobeExec[system()] = which("ffprobe") # Use the system version if bundled version not found

# Interpolation Defaults
dainGpuId = "auto"
dainThreads = "1:1:1"
dainTileSize = "256"
cainTileSize = "512"


def DainVulkanFileModeCommand(input0File, input1File, outputFile, time_step="0.5",
                              tile_size=dainTileSize, gpu_id=dainGpuId, threads=dainThreads):
    pathlib.Path(os.path.dirname(outputFile)).mkdir(parents=True, exist_ok=True)  # Create parent folder of outputFile
    command = [dainNcnnExec[system()], "-0", os.path.abspath(input0File), "-1", os.path.abspath(input1File),
               "-o", os.path.abspath(outputFile), "-s", time_step, "-t", tile_size, "-g", gpu_id,
               "-j", threads]
    subprocess.run(command, cwd=dainNcnnExecDirectory)


def DainVulkanFolderModeCommand(inputFolder, outputFolder, targetFrames,
                                tile_size=dainTileSize, gpu_id=dainGpuId, threads=dainThreads):
    pathlib.Path(outputFolder).mkdir(parents=True, exist_ok=True)  # Create outputFolder
    command = [dainNcnnExec[system()], "-i", os.path.abspath(inputFolder), "-o", os.path.abspath(outputFolder),
               "-n", targetFrames, "-t", tile_size, "-g", gpu_id, "-j", threads]
    subprocess.run(command, cwd=dainNcnnExecDirectory)


def CainVulkanFileModeCommand(input0File, input1File, outputFile,
                              tile_size=cainTileSize, gpu_id=dainGpuId, threads=dainThreads): # Doesn't support timestep
    pathlib.Path(os.path.dirname(outputFile)).mkdir(parents=True, exist_ok=True)  # Create parent folder of outputFile
    command = [cainNcnnExec[system()], "-0", os.path.abspath(input0File), "-1", os.path.abspath(input1File),
               "-o", os.path.abspath(outputFile), "-t", tile_size, "-g", gpu_id, "-j", threads]
    subprocess.run(command, cwd=cainNcnnExecDirectory)


def CainVulkanFolderModeCommand(inputFolder, outputFolder,
                                tile_size=cainTileSize, gpu_id=dainGpuId, threads=dainThreads):
    pathlib.Path(outputFolder).mkdir(parents=True, exist_ok=True)  # Create outputFolder
    command = [cainNcnnExec[system()], "-i", os.path.abspath(inputFolder), "-o", os.path.abspath(outputFolder),
               "-t", tile_size, "-g", gpu_id, "-j", threads]
    subprocess.run(command, cwd=cainNcnnExecDirectory)

# FFmpeg Process Functions
def FfmpegExtractFrames(inputFile, outputFolder):  # "Step 1"
    # ffmpeg -i "$i" %06d.png
    '''
    for -vsync: "crf" will use "r_frame_rate", "vfr" will use "avg_frame_rate"
    '''
    pathlib.Path(outputFolder).mkdir(parents=True, exist_ok=True) # Create outputFolder
    command = [ffmpegExec[system()], "-i", inputFile, "-loglevel", "error", "-vsync", "cfr", os.path.join(outputFolder, "%06d.png")]
    subprocess.run(command)


def FfmpegEncodeFrames(inputFolder, outputFile, framerate):
    # ffmpeg -framerate 48 -i interpolated_frames/%06d.png output.mp4
    pathlib.Path(os.path.dirname(outputFile)).mkdir(parents=True, exist_ok=True) # Create parent folder of outputFile
    command = [ffmpegExec[system()], "-framerate", framerate, "-i", os.path.join(inputFolder, "%06d.png"), "-crf", "18", "-y",
               "-loglevel", "error", outputFile]
    subprocess.run(command)

#FFprobe Process Functions
def FfprobeCollectVideoInfo(inputFile):
    # ffprobe -show_streams -count_frames -select_streams v:0 -print_format json -loglevel quiet input.mp4
    '''
    Some videos don't return "duration" and "nb_frames" such as apng
    "-count_frames" returns "nb_read_frames" for every format though
    "nb_read_frames" won't be accurate if the input video is vfr

    http://svn.ffmpeg.org/doxygen/trunk/structAVStream.html
    "avg_frame_rate" is "Average framerate" aka: duration/framecount
    "r_frame_rate" is "Real base framerate" which is the lowest common framerate of all frames in the video
    '''
    command = [ffprobeExec[system()], "-show_streams", "-count_frames", "-select_streams", "v:0",
               "-print_format", "json", "-loglevel", "quiet", inputFile]
    output = subprocess.check_output(command, universal_newlines=True)
    parsedOutput = json.loads(output)["streams"][0]
    return({
        "width": parsedOutput["width"],
        "height": parsedOutput["height"],
        "fpsReal": parsedOutput["r_frame_rate"],
        "fpsAverage": parsedOutput["avg_frame_rate"],
        "frameCount": parsedOutput["nb_read_frames"]
    })


def FfprobeCollectFrameInfo(inputFile):
    # ffprobe -show_packets -select_streams v:0 -print_format json -loglevel quiet input.mp4
    command = [ffprobeExec[system()], "-show_packets", "-select_streams", "v:0", "-print_format", "json", "-loglevel", "quiet",
               inputFile]
    output = subprocess.check_output(command, universal_newlines=True)
    parsedOutput = json.loads(output)["packets"]
    return(parsedOutput)


def CainFolderMultiplierHandler(inputFolder, outputFolder, multiplier):
    folderParent = pathlib.Path(outputFolder).parent
    multiplierInternal = 1
    cainFolderFrom = inputFolder
    while multiplierInternal < multiplier:
        multiplierInternal = multiplierInternal * 2
        print("From:", cainFolderFrom)
        cainFolderTo = os.path.join(folderParent, ("cain-" + str(multiplierInternal) + "x"))
        print("To:", cainFolderTo)
        print("Interpolating to:", str(multiplierInternal) + "x")
        CainVulkanFolderModeCommand(cainFolderFrom, cainFolderTo)
        cainFolderFrom = cainFolderTo
    print("Renaming", cainFolderTo, "to", outputFolder)
    os.rename(cainFolderTo, outputFolder)

if __name__ == "__main__":
    # Console arguments
    parser = argparse.ArgumentParser()
    ## Path Arguments
    parser.add_argument("-i", "--input-file", help="Path to input video", action="store", required=True)
    parser.add_argument("-o", "--output-file", help="Path to output final video to", action="store")
    parser.add_argument("-O", "--output-folder", help="Folder to output work to", action="store", required=True)
    ## Interpolation options
    parser.add_argument("-m", "--frame-multiplier", help="Frame multiplier 2x,3x,etc (default=2)", action="store",
                        type=int, default=2)
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
    parser.add_argument("--input-fps", help="Manually specify framerate of input video", action="store", type=float)
    parser.add_argument("--verbose", help="Print additional info to the commandline", action="store_true")
    args = vars(parser.parse_args())

    # Override global variables with arguments
    if args["gpu_id"] is not None:
        dainGpuId = args["gpu_id"]
    if args["thread_count"] is not None:
        dainThreads = args["thread_count"]
    if args["tilesize"] is not None:
        dainTileSize = args["tilesize"]

    if args["steps"] is None:
        stepsSelection = None
    else:
        stepsSelection = args["steps"].split(",")

    print("GPU Selection:", dainGpuId)
    print("Threads:", dainThreads)
    print("Tilesize:", dainTileSize)
    if args["verbose"] is True:
        print("Platform:", system())

    inputFile = os.path.abspath(args["input_file"])
    outputFolder = os.path.abspath(args["output_folder"])
    print("Input file:", inputFile)

    print("FFprobe: Scanning video metadata...")
    inputFileProperties = FfprobeCollectVideoInfo(inputFile)
    print(inputFileProperties)
    if args["input_fps"] is not None:
        inputFileFps = args["input_fps"]
    else:
        fracNum, fracDenom = inputFileProperties["fpsReal"].split("/")
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
    folderInterpolatedFramesCount = folderOriginalFramesCount * args["frame_multiplier"]
    print("Interpolated frame count", folderInterpolatedFramesCount)

    if (stepsSelection is None) or ("2" in stepsSelection):
        print("Step 2: Processing frames to interpolated_frames using", args["interpolator"])
        if args["interpolator"] == "dain-ncnn":
            print("Interpolation Multiplier:", args["frame_multiplier"])
            DainVulkanFolderModeCommand(folderOriginalFrames,
                                        folderInterpolatedFrames,
                                        str(folderInterpolatedFramesCount))
        elif args["interpolator"] == "cain-ncnn":
            CainFolderMultiplierHandler(folderOriginalFrames, folderInterpolatedFrames, args["frame_multiplier"])
            # CainVulkanFolderModeCommand(folderOriginalFrames, folderInterpolatedFrames)
        else:
            print("Invalid interpolator option")
            exit(1)

    if (stepsSelection is None) or ("3" in stepsSelection):
        print("Step 3: Extracting frames to output_videos")
        FfmpegEncodeFrames(folderInterpolatedFrames, os.path.join(folderOutputVideos, "output.mp4"),
                           str(inputFileFps * args["frame_multiplier"]))
