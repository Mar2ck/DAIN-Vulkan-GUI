#!/usr/bin/env python3
"""
DAIN-Vulkan-GUI: CLI Frontend

AI-Powered video interpolater (eg. 30fps -> 60fps) for Vulkan devices. Based on dain-ncnn-vulkan and ffmpeg

This file is the core of the DAIN-Vulkan-GUI project and it's command-line interface
"""
# Built-in modules
import argparse
import json
import logging
import os
import pathlib
from platform import system
import shutil
import subprocess
# Local modules
import locations
# import image_similarity

# Interpolation Defaults
dainGpuId = "auto"
dainThreads = "1:1:1"
dainTileSize = "256"
cainTileSize = "512"

# Dain-ncnn Process Functions
def DainVulkanFileModeCommand(input0File, input1File, outputFile, time_step=None):
    pathlib.Path(os.path.dirname(outputFile)).mkdir(parents=True, exist_ok=True)  # Create parent folder of outputFile
    command = [locations.DAIN_NCNN_VULKAN_BIN, "-0", os.path.abspath(input0File), "-1", os.path.abspath(input1File),
               "-o", os.path.abspath(outputFile), "-s", time_step, "-t", dainTileSize, "-g", dainGpuId,
               "-j", dainThreads]
    subprocess.run(command, cwd=locations.DAIN_NCNN_VULKAN_LOCATION)


def DainVulkanFolderModeCommand(inputFolder, outputFolder, targetFrames):
    if os.path.isdir(outputFolder) is True:  # Delete output folder if it exists already
        print("\"{}\" already exists, deleting".format(outputFolder))
        shutil.rmtree(outputFolder)
    pathlib.Path(outputFolder).mkdir(parents=True, exist_ok=True)  # Create outputFolder
    command = [locations.DAIN_NCNN_VULKAN_BIN, "-i", os.path.abspath(inputFolder), "-o", os.path.abspath(outputFolder),
               "-n", targetFrames, "-t", dainTileSize, "-g", dainGpuId, "-j", dainThreads]
    subprocess.run(command, cwd=locations.DAIN_NCNN_VULKAN_LOCATION)

# Cain-ncnn Process Functions
def CainVulkanFileModeCommand(input0File, input1File, outputFile): # Doesn't support timestep
    pathlib.Path(os.path.dirname(outputFile)).mkdir(parents=True, exist_ok=True)  # Create parent folder of outputFile
    command = [locations.CAIN_NCNN_VULKAN_BIN, "-0", os.path.abspath(input0File), "-1", os.path.abspath(input1File),
               "-o", os.path.abspath(outputFile), "-t", cainTileSize, "-g", dainGpuId, "-j", dainThreads]
    subprocess.run(command, cwd=locations.CAIN_NCNN_VULKAN_LOCATION)


def CainVulkanFolderModeCommand(inputFolder, outputFolder):
    pathlib.Path(outputFolder).mkdir(parents=True, exist_ok=True)  # Create outputFolder
    command = [locations.CAIN_NCNN_VULKAN_BIN, "-i", os.path.abspath(inputFolder), "-o", os.path.abspath(outputFolder),
               "-t", cainTileSize, "-g", dainGpuId, "-j", dainThreads]
    # print(" ".join(command))
    subprocess.run(command, cwd=locations.CAIN_NCNN_VULKAN_LOCATION)

# FFmpeg Process Functions
def FfmpegExtractFrames(inputFile, outputFolder):  # "Step 1"
    # ffmpeg -i "$i" %06d.png
    '''
    for -vsync: "crf" will use "r_frame_rate", "vfr" will use "avg_frame_rate"
    '''
    pathlib.Path(outputFolder).mkdir(parents=True, exist_ok=True) # Create outputFolder
    command = [locations.FFMPEG_BIN, "-i", inputFile, "-loglevel", "error", "-vsync", "cfr",
               os.path.join(outputFolder, "%06d.png")]
    subprocess.run(command)


def FfmpegEncodeFrames(inputFolder, outputFile, framerate):
    # ffmpeg -framerate 48 -i interpolated_frames/%06d.png output.mp4
    pathlib.Path(os.path.dirname(outputFile)).mkdir(parents=True, exist_ok=True) # Create parent folder of outputFile
    command = [locations.FFMPEG_BIN, "-framerate", framerate, "-i", os.path.join(inputFolder, "%06d.png"), "-crf", "18",
               "-y", "-loglevel", "error", outputFile]
    # print("Executing:", " ".join(command))
    subprocess.run(command)

# FFprobe Process Functions
def FfprobeCollectVideoInfo(inputFile):
    # ffprobe -show_streams -select_streams v:0 -print_format json -loglevel quiet input.mp4
    '''
    Some videos don't return "duration" and "nb_frames" such as apng
    "nb_read_frames" won't be accurate if the input video is vfr

    http://svn.ffmpeg.org/doxygen/trunk/structAVStream.html
    "avg_frame_rate" is "Average framerate" aka: duration/framecount
    "r_frame_rate" is "Real base framerate" which is the lowest common framerate of all frames in the video
    '''
    command = [locations.FFPROBE_BIN, "-show_streams", "-select_streams", "v:0",
               "-print_format", "json", "-loglevel", "quiet", inputFile]
    output = subprocess.check_output(command, universal_newlines=True)
    parsedOutput = json.loads(output)["streams"][0]
    return({
        "width": parsedOutput["width"],
        "height": parsedOutput["height"],
        "fpsReal": parsedOutput["r_frame_rate"],
        "fpsAverage": parsedOutput["avg_frame_rate"]})


def FfprobeCollectFrameInfo(inputFile):
    # ffprobe -show_packets -select_streams v:0 -print_format json -loglevel quiet input.mp4
    command = [locations.FFPROBE_BIN, "-show_packets", "-select_streams", "v:0", "-print_format", "json",
               "-loglevel", "quiet", inputFile]
    output = subprocess.check_output(command, universal_newlines=True)
    parsedOutput = json.loads(output)["packets"]
    return(parsedOutput)


def CainFolderMultiplierHandler(inputFolder, outputFolder, multiplier):
    folderParent = pathlib.Path(outputFolder).parent
    multiplierInternal = 1
    cainFolderFrom = inputFolder
    if multiplier <= 1:
        raise ValueError("Multiplier must be higher than 1")
    else:
        if not ((multiplier & (multiplier-1) == 0) and multiplier != 0):  # Check if not a power of 2
            raise ValueError("Multiplier must be a power of 2 (2, 4, 8, etc.)")
        else:
            cainOutputFolders = []
            while multiplierInternal < multiplier:
                multiplierInternal = multiplierInternal * 2
                print("Interpolating to:", str(multiplierInternal) + "x")

                print("From: \"{}\"".format(cainFolderFrom))
                cainFolderTo = os.path.join(folderParent, ("cain-" + str(multiplierInternal) + "x"))
                cainOutputFolders.append(cainFolderTo)
                print("To: \"{}\"".format(cainFolderTo))

                CainVulkanFolderModeCommand(cainFolderFrom, cainFolderTo)
                cainFolderFrom = cainFolderTo  # Set last output folder to the input folder for the next loop
            print("Renaming \"{}\" to \"{}\"".format(cainFolderTo, outputFolder))
            if os.path.isdir(outputFolder) is True:
                print("\"{}\" already exists, deleting".format(outputFolder))
                shutil.rmtree(outputFolder)
            os.rename(cainFolderTo, outputFolder)
            if cainOutputFolders[:-1]:
                print("Deleting leftover folders:", cainOutputFolders[:-1])
                for folder in cainOutputFolders[:-1]:
                    shutil.rmtree(folder)

if __name__ == "__main__":
    # Console arguments
    parser = argparse.ArgumentParser()
    ## Path options
    parser.add_argument("-i", "--input-file", required=True, help="Path to input video")
    parser.add_argument("-o", "--output-file", help="Path to output final video to")
    parser.add_argument("-O", "--output-folder", required=True, help="Folder to output work to", )
    ## Interpolation options
    parser.add_argument("-m", "--frame-multiplier", type=int, default=2, help="Frame multiplier 2x,3x,etc (default=2)")
    parser.add_argument("--target-fps", help="[Unimplemented] Calculates frame multiplier based on a target framerate")
    parser.add_argument("--interpolator", default="dain-ncnn", help="Pick interpolator: dain-ncnn, cain-ncnn "
                                                                    "(default=dain-ncnn)")
    ## Dain-ncnn/Cain-ncnn pass-through options
    parser.add_argument("-g", "--gpu-id", help="GPU to use (default=auto) can be 0,1,2 for multi-gpu")
    parser.add_argument("-t", "--tilesize", help="Tile size (>=128, default=256) must be multiple of 32, "
                                                 "can be 256,256,128 for multi-gpu")
    parser.add_argument("-j", "--thread-count", help="Thread count for load/process/save (default=1:2:2) can be "
                                                     "1:2,2,2:2 for multi-gpu")
    ## Step options
    parser.add_argument("--steps", help="If specified only run certain steps 1,2,3 (eg. 1,2 for 1 & 2 only)")
    ## Output file options
    parser.add_argument("--video-type", default="mp4", help="Video type for output video eg. mp4, webm, mkv "
                                                            "(default=mp4)")
    ## Debug options
    parser.add_argument("--input-fps", type=float, help="Manually specify framerate of input video")
    parser.add_argument("--verbose", action="store_true", help="Print additional info to the commandline")
    parser.add_argument("--debug", action="store_true", help="Print debug messages to the commandline")
    args = vars(parser.parse_args())

    # Logging
    if args["verbose"] is True:
        logging.basicConfig(level=logging.INFO)
    if args["debug"] is True:
        logging.basicConfig(level=logging.DEBUG)

    # Print interpolator options to terminal/Override interpolation defaults with arguments if specified
    if args["gpu_id"] is not None:
        dainGpuId = args["gpu_id"]
    logging.info("GPU Selection: \"{}\"".format(dainGpuId))

    if args["thread_count"] is not None:
        dainThreads = args["thread_count"]
    print("Threads:", dainThreads)
    if args["tilesize"] is not None:
        dainTileSize = args["tilesize"]
        cainTileSize = args["tilesize"]
    print("Tilesize:", dainTileSize)
    print("Platform:", system())

    # Steps
    if args["steps"] is None:
        stepsSelection = None
    else:
        stepsSelection = args["steps"].split(",")

    # Input/Output Variables
    inputFile = os.path.abspath(args["input_file"])
    print("Input file:", inputFile)
    inputFileName = pathlib.Path(inputFile).stem  # Filename of input file without extension
    outputFolder = os.path.abspath(args["output_folder"])
    inputFileNameSuffixes = []

    # Use specified fps or grab fps from input file
    if args["input_fps"] is not None:
        inputFileFps = args["input_fps"]
    else:
        print("FFprobe: Scanning video metadata for framerate...")
        inputFileProperties = FfprobeCollectVideoInfo(inputFile)
        print(inputFileProperties)
        fracNum, fracDenom = inputFileProperties["fpsReal"].split("/")
        inputFileFps = int(fracNum) / int(fracDenom)

    # Setup working folder and predefined output folders
    folderBase = os.path.join(outputFolder, inputFileName)
    print("Working Directory:", folderBase)
    folderOriginalFrames = os.path.join(folderBase, "original_frames")
    folderInterpolatedFrames = os.path.join(folderBase, "interpolated_frames")
    folderOutputVideos = os.path.join(folderBase, "output_videos")

    # Step 1: Original Video -> Original Frames
    if (stepsSelection is None) or ("1" in stepsSelection):
        print("Step 1: Extracting frames to original_frames")
        FfmpegExtractFrames(inputFile, folderOriginalFrames)

    # Count original frames
    folderOriginalFramesCount = len(sorted(os.listdir(folderOriginalFrames)))
    print("Original frame count:", folderOriginalFramesCount)
    # Calculate interpolated frames by multiplying original frames
    folderInterpolatedFramesCount = folderOriginalFramesCount * args["frame_multiplier"]
    print("Interpolated frame count", folderInterpolatedFramesCount)

    # Step 2: Original Frames -> Interpolated Frames
    if (stepsSelection is None) or ("2" in stepsSelection):
        print("Step 2: Processing frames to interpolated_frames using", args["interpolator"])
        if args["interpolator"] == "dain-ncnn":
            print("Interpolating to: {}x".format(args["frame_multiplier"]))
            DainVulkanFolderModeCommand(folderOriginalFrames,
                                        folderInterpolatedFrames,
                                        str(folderInterpolatedFramesCount))
        elif args["interpolator"] == "cain-ncnn":
            CainFolderMultiplierHandler(folderOriginalFrames, folderInterpolatedFrames, args["frame_multiplier"])
            # CainVulkanFolderModeCommand(folderOriginalFrames, folderInterpolatedFrames)
        else:
            print("Invalid interpolator option")
            exit(1)

    # Set filename suffix even if step 2 skipped
    if args["interpolator"] == "dain-ncnn":
        inputFileNameSuffixes.append("-Dain{}x".format(args["frame_multiplier"]))
    elif args["interpolator"] == "cain-ncnn":
        inputFileNameSuffixes.append("-Cain{}x".format(args["frame_multiplier"]))
    else:
        print("Invalid interpolator option")
        exit(1)

    # Step 3: Interpolated Frames -> Output Video
    if (stepsSelection is None) or ("3" in stepsSelection):
        print("Step 3: Extracting frames to output_videos")
        FfmpegEncodeFrames(folderInterpolatedFrames,
                           os.path.join(folderOutputVideos, inputFileName + "".join(inputFileNameSuffixes) + "."
                                        + args["video_type"]),
                           str(inputFileFps * args["frame_multiplier"]))
