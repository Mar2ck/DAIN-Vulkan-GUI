#!/usr/bin/env python3
"""
DAIN-Vulkan-GUI: CLI Frontend
AI-Powered video interpolater (eg. 30fps -> 60fps) for Vulkan devices. Based on dain-ncnn-vulkan and ffmpeg
"""
# Built-in modules
import argparse
import json
import logging
import os
import pathlib
from platform import system
import shutil

# Local modules
import definitions
import dain_ncnn_vulkan
# import cain_ncnn_vulkan
import ffmpeg
import ffprobe
# import video_extract
import interpolator
import image_similarity


def main(input_file, output_folder, **kwargs):
    # System Info
    print("Platform:", system())

    # Set defaults for kwargs (argparse adds unused arguements to the dict even if unused)
    frame_multiplier = definitions.DEFAULT_FRAME_MULTIPLIER
    if ("frame_multiplier" in kwargs) and (kwargs["frame_multiplier"] is not None):
        frame_multiplier = kwargs["frame_multiplier"]
    interpolator_engine = definitions.DEFAULT_INTERPOLATOR_ENGINE
    if ("interpolator_engine" in kwargs) and (kwargs["interpolator_engine"] is not None):
        interpolator_engine = kwargs["interpolator_engine"]
    video_type = definitions.DEFAULT_VIDEO_TYPE
    if ("video_type" in kwargs) and (kwargs["video_type"] is not None):
        video_type = kwargs["video_type"]
    loop_frames = definitions.DEFAULT_LOOP
    if ("loop_video" in kwargs) and (kwargs["loop_video"] is not None):
        loop_frames = kwargs["loop_video"]

    # Optional arguments for interpolators
    interpolatorOptions = {}
    if ("tile_size" in kwargs) and (kwargs["tile_size"] is not None):
        interpolatorOptions["tile_size"] = kwargs["tile_size"]
    if ("gpu_id" in kwargs) and (kwargs["gpu_id"] is not None):
        interpolatorOptions["gpu_id"] = kwargs["gpu_id"]
    if ("threads" in kwargs) and (kwargs["threads"] is not None):
        interpolatorOptions["threads"] = kwargs["threads"]
    print("Interpolator Options:", interpolatorOptions)

    # Parse step selection
    stepsSelection = None
    if ("steps" in kwargs) and (kwargs["steps"] is not None):
        stepsSelection = kwargs["steps"].split(",")
        print("Steps selected:", stepsSelection)

    # Input/Output Videos
    inputFile = os.path.abspath(input_file)
    inputFileName = pathlib.Path(inputFile).stem  # Filename of input file without extension
    outputFolder = os.path.abspath(output_folder)
    print("Input file:", inputFile)

    # Input FPS, prioritize specified over detected
    if ("input_fps" in kwargs) and (kwargs["input_fps"] is not None):
        inputFileFps = kwargs["input_fps"]
    else:
        print("FFprobe: Scanning video metadata for framerate...")
        inputFileProperties = ffprobe.analyze_video_stream_metadata(inputFile)
        print(inputFileProperties)
        fracNum, fracDenom = inputFileProperties["fpsReal"].split("/")
        inputFileFps = int(fracNum) / int(fracDenom)

    # Setup working folder and predefined output folders
    folderBase = os.path.join(outputFolder, inputFileName)
    pathlib.Path(folderBase).mkdir(parents=True, exist_ok=True)  # Create base folder at start
    print("Working Directory:", folderBase)
    folderOriginalFrames = os.path.join(folderBase, "original_frames")
    folderInterpolatedFrames = os.path.join(folderBase, "interpolated_frames")
    folderOutputVideos = os.path.join(folderBase, "output_videos")
    infoJsonFilePath = os.path.join(folderBase, "info.json")

    # Read info from json
    infoJsonFile = {}
    if os.path.isfile(infoJsonFilePath):
        try:
            infoJsonFile = json.load(open(infoJsonFilePath, 'r'))
            print("info.json read:", infoJsonFile)
        except ValueError:
            print("info.json not read")
    else:
        print("Creating info.json")
        pathlib.Path(infoJsonFilePath).touch()

    # Step 1: Original Video -> Original Frames
    if (stepsSelection is None) or ("1" in stepsSelection):
        print("\nStep 1: Extracting frames to original_frames")
        ffmpeg.extract_frames(inputFile, folderOriginalFrames)
        folderOriginalFramesExtractedCount = len(os.listdir(folderOriginalFrames))
        infoJsonFile["extracted_frames"] = folderOriginalFramesExtractedCount
        print("Extracted frame count:", folderOriginalFramesExtractedCount)

        if ("duplicate_auto_delete" in kwargs) and (kwargs["duplicate_auto_delete"] is not None):
            print("Auto-deleting original_frames over {} similarity...".format(kwargs["duplicate_auto_delete"]))
            image_similarity.delete_similar_images(folderOriginalFrames, kwargs["duplicate_auto_delete"])

        # print("Removing alpha layer from original_frames...")
        # video_extract.png_directory_remove_alpha_channel(folderOriginalFrames)

    print("original_frames count:", len(os.listdir(folderOriginalFrames)))

    # Step 2: Original Frames -> Interpolated Frames
    if (stepsSelection is None) or ("2" in stepsSelection):
        print("\nStep 2: Processing frames to interpolated_frames using", interpolator_engine)
        print("Interpolating to: {}x".format(frame_multiplier))

        infoJsonFile["outputSuffixes"] = []  # Overwrite suffixes since step 2 is ran
        currentInterpolatorFolder = folderOriginalFrames

        # Dynamic interpolation
        if ("interpolation_mode" in kwargs) and (kwargs["interpolation_mode"] == "dynamic"):
            folderDynamic = os.path.join(folderBase, "dynamic-1x")
            interpolator.interpolate_dynamic(currentInterpolatorFolder, folderDynamic, infoJsonFile["extracted_frames"],
                                             loop=loop_frames, **interpolatorOptions)

            currentInterpolatorFolder = folderDynamic
            infoJsonFile["outputSuffixes"].append("-Dynamic1x".format(frame_multiplier))

        # Static interpolation
        if frame_multiplier >= 2:
            folderInterpolatedFramesCount = len(os.listdir(folderOriginalFrames)) * frame_multiplier
            print("interpolated_frames count", folderInterpolatedFramesCount)
            if interpolator_engine.startswith("dain-ncnn"):
                dain_ncnn_vulkan.interpolate_folder_mode(currentInterpolatorFolder, folderInterpolatedFrames,
                                                         frame_multiplier, **interpolatorOptions)
                currentInterpolatorFolder = folderInterpolatedFrames
                infoJsonFile["outputSuffixes"].append("-Dain{}x".format(frame_multiplier))
            elif interpolator_engine.startswith("cain-ncnn"):
                interpolator.cain_folder_multiplier_handler(currentInterpolatorFolder, folderInterpolatedFrames,
                                                            frame_multiplier, **interpolatorOptions)
                currentInterpolatorFolder = folderInterpolatedFrames
                infoJsonFile["outputSuffixes"].append("-Cain{}x".format(frame_multiplier))
            else:
                print("Invalid interpolator option")
                exit(1)

        # Rename last folder to interpolated_frames if not already
        if currentInterpolatorFolder is not folderInterpolatedFrames:
            if os.path.isdir(folderInterpolatedFrames) is True:
                print("\"{}\" already exists, deleting".format(folderInterpolatedFrames))
                shutil.rmtree(folderInterpolatedFrames)
            os.rename(currentInterpolatorFolder, folderInterpolatedFrames)

    # Step 3: Interpolated Frames -> Output Video
    if (stepsSelection is None) or ("3" in stepsSelection):
        print("\nStep 3: Extracting frames to output_videos")
        ffmpeg.encode_frames(folderInterpolatedFrames,
                             os.path.join(folderOutputVideos, inputFileName + "".join(infoJsonFile["outputSuffixes"]) +
                                          "." + video_type),
                             str(inputFileFps * frame_multiplier))

    # Write info to json at the end
    json.dump(infoJsonFile, open(infoJsonFilePath, "w"))


if __name__ == "__main__":
    # Console arguments
    parser = argparse.ArgumentParser()
    # Path options
    parser.add_argument("-i", "--input-file", required=True, help="Path to input video")
    parser.add_argument("-O", "--output-folder", required=True, help="Folder to output work to")
    parser.add_argument("-o", "--output-file", help="[Unimplemented] Path to output final video to")
    # Interpolation options
    parser.add_argument("--interpolation-mode", default=definitions.DEFAULT_INTERPOLATOR_MODE,
                        help="Interpolation type (static/dynamic, default=static)")
    parser.add_argument("-m", "--frame-multiplier", type=int, default=definitions.DEFAULT_FRAME_MULTIPLIER,
                        help="Frame multiplier 2x,3x,etc (default=2)")
    parser.add_argument("--target-fps", help="[Unimplemented] Calculates frame multiplier based on a target framerate")
    parser.add_argument("-e", "--interpolator-engine", default=definitions.DEFAULT_INTERPOLATOR_ENGINE,
                        help="Pick interpolator: dain-ncnn, cain-ncnn (default=dain-ncnn)")
    parser.add_argument("--loop-video", action="store_true",
                        help="[Unimplemented] Interpolates video as a loop (last frame leads into the first)")
    parser.add_argument("--duplicate-auto-delete", type=float,
                        help="Based on a percentage (Eg. 0.95) will delete any frames found to be more similar")
    # Dain-ncnn/Cain-ncnn pass-through options
    parser.add_argument("-g", "--gpu-id", help="GPU to use (default=auto) can be 0,1,2 for multi-gpu")
    parser.add_argument("-t", "--tile-size",
                        help="Tile size (>=128, default=256) must be multiple of 32, can be 256,256,128 for multi-gpu")
    parser.add_argument("-j", "--threads",
                        help="Thread count for load/process/save (default=1:2:2) can be 1:2,2,2:2 for multi-gpu")
    # Step options
    parser.add_argument("--steps", help="If specified only run certain steps 1,2,3 (eg. 1,2 for 1 & 2 only)")
    # Output file options
    parser.add_argument("--video-type", default=definitions.DEFAULT_VIDEO_TYPE,
                        help="Video type for output video eg. mp4, webm, mkv (default=mp4)")
    # Debug options
    parser.add_argument("--input-fps", type=float, help="Manually specify framerate of input video")
    parser.add_argument("--verbose", action="store_true", help="Print additional info to the commandline")
    parser.add_argument("--debug", action="store_true", help="Print debug messages to the commandline")
    arguments = vars(parser.parse_args())

    # Logging
    if arguments["verbose"] is True:
        logging.basicConfig(level=logging.INFO)
    if arguments["debug"] is True:
        logging.basicConfig(level=logging.DEBUG)

    main(**arguments)
