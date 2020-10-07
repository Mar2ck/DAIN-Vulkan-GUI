#!/usr/bin/env python3
"""
DAIN-Vulkan-GUI: CLI Frontend

AI-Powered video interpolater (eg. 30fps -> 60fps) for Vulkan devices. Based on dain-ncnn-vulkan and ffmpeg

This file is the core of the DAIN-Vulkan-GUI project and it's command-line interface
"""
# Built-in modules
import argparse
import logging
import os
import pathlib
from platform import system
# Local modules
import dain_ncnn_vulkan
# import cain_ncnn_vulkan
import ffmpeg
import ffprobe
import interpolator
# import image_similarity

# Interpolation Defaults
dainTileSize = "256"
cainTileSize = "512"
dainGpuId = "auto"
dainThreads = "1:1:1"

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
        inputFileProperties = ffprobe.analyze_video_stream_metadata(inputFile)
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
        ffmpeg.extract_frames(inputFile, folderOriginalFrames)

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
            dain_ncnn_vulkan.interpolate_folder_mode(folderOriginalFrames, folderInterpolatedFrames,
                                                     args["frame_multiplier"],
                                                     tile_size=dainTileSize, gpuid=dainGpuId, threads=dainThreads)
        elif args["interpolator"] == "cain-ncnn":
            interpolator.cain_folder_multiplier_handler(folderOriginalFrames, folderInterpolatedFrames,
                                                        args["frame_multiplier"],
                                                        tile_size=cainTileSize, gpuid=dainGpuId, threads=dainThreads)
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
        ffmpeg.encode_frames(folderInterpolatedFrames,
                             os.path.join(folderOutputVideos, inputFileName + "".join(inputFileNameSuffixes) +
                                          "." + args["video_type"]),
                             str(inputFileFps * args["frame_multiplier"]))
