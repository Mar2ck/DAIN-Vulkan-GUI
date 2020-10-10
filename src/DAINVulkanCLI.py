#!/usr/bin/env python3
"""
DAIN-Vulkan-GUI: CLI Frontend
AI-Powered video interpolater (eg. 30fps -> 60fps) for Vulkan devices. Based on dain-ncnn-vulkan and ffmpeg
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
import image_similarity

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
    parser.add_argument("--interpolator", default="dain-ncnn",
                        help="Pick interpolator: dain-ncnn, cain-ncnn (default=dain-ncnn)")
    parser.add_argument("--duplicate-auto-delete", type=float,
                        help="Based on a percentage (Eg. 0.95) will delete any frames found to be more similar")
    ## Dain-ncnn/Cain-ncnn pass-through options
    parser.add_argument("-g", "--gpu-id", help="GPU to use (default=auto) can be 0,1,2 for multi-gpu")
    parser.add_argument("-t", "--tilesize",
                        help="Tile size (>=128, default=256) must be multiple of 32, can be 256,256,128 for multi-gpu")
    parser.add_argument("-j", "--threads",
                        help="Thread count for load/process/save (default=1:2:2) can be 1:2,2,2:2 for multi-gpu")
    ## Step options
    parser.add_argument("--steps", help="If specified only run certain steps 1,2,3 (eg. 1,2 for 1 & 2 only)")
    ## Output file options
    parser.add_argument("--video-type", default="mp4",
                        help="Video type for output video eg. mp4, webm, mkv (default=mp4)")
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

    # System Info
    print("Platform:", system())

    # Optional arguments for interpolators
    interpolatorOptions = {}
    if args["tilesize"] is not None:
        interpolatorOptions["tile_size"] = args["tilesize"]
    if args["gpu_id"] is not None:
        interpolatorOptions["gpu_id"] = args["gpu_id"]
    if args["threads"] is not None:
        interpolatorOptions["threads"] = args["threads"]
    print("Interpolator Options:", interpolatorOptions)

    # Parse step selection
    stepsSelection = None if args["steps"] is None else args["steps"].split(",")  # Steps

    # Input/Output Videos
    inputFile = os.path.abspath(args["input_file"])
    inputFileName = pathlib.Path(inputFile).stem  # Filename of input file without extension
    outputFolder = os.path.abspath(args["output_folder"])
    print("Input file:", inputFile)

    # Define suffixes to add to final filename
    outputFileNameSuffixes = []

    # Input FPS, prioritize specified over detected
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
        # folderOriginalFramesExtractedCount = len(sorted(os.listdir(folderOriginalFrames)))
        if args["duplicate_auto_delete"] is not None:
            print("Auto deleting frames with more then {} similarity".format(args["duplicate_auto_delete"]))
            image_similarity.delete_similar_images(folderOriginalFrames, args["duplicate_auto_delete"])

    # Count original frames (assumes step 1 was ran)
    folderOriginalFramesCount = len(sorted(os.listdir(folderOriginalFrames)))
    print("Original frame count:", folderOriginalFramesCount)
    folderInterpolatedFramesCount = folderOriginalFramesCount * args["frame_multiplier"]
    print("Interpolated frame count", folderInterpolatedFramesCount)

    # Step 2: Original Frames -> Interpolated Frames
    if (stepsSelection is None) or ("2" in stepsSelection):
        print("Step 2: Processing frames to interpolated_frames using", args["interpolator"])
        print("Interpolating to: {}x".format(args["frame_multiplier"]))
        if args["interpolator"].startswith("dain-ncnn"):
            dain_ncnn_vulkan.interpolate_folder_mode(folderOriginalFrames, folderInterpolatedFrames,
                                                     args["frame_multiplier"], **interpolatorOptions)
        elif args["interpolator"].startswith("cain-ncnn"):
            interpolator.cain_folder_multiplier_handler(folderOriginalFrames, folderInterpolatedFrames,
                                                        args["frame_multiplier"], **interpolatorOptions)
        else:
            print("Invalid interpolator option")
            exit(1)

    # Set filename suffix even if step 2 skipped
    if args["interpolator"].startswith("dain-ncnn"):
        outputFileNameSuffixes.append("-Dain{}x".format(args["frame_multiplier"]))
    elif args["interpolator"].startswith("cain-ncnn"):
        outputFileNameSuffixes.append("-Cain{}x".format(args["frame_multiplier"]))
    else:
        print("Invalid interpolator option")
        exit(1)

    # Step 3: Interpolated Frames -> Output Video
    if (stepsSelection is None) or ("3" in stepsSelection):
        print("Step 3: Extracting frames to output_videos")
        ffmpeg.encode_frames(folderInterpolatedFrames,
                             os.path.join(folderOutputVideos, inputFileName + "".join(outputFileNameSuffixes) +
                                          "." + args["video_type"]),
                             str(inputFileFps * args["frame_multiplier"]))
