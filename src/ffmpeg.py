"""
FFmpeg process wrapper
"""
# Built-in modules
import logging
import os
import pathlib
import subprocess
# Local modules
import definitions


def extract_frames(input_file, output_folder):  # "Step 1"
    """Extract video frames to a folder
    for -vsync: "crf" will use "r_frame_rate", "vfr" will use "avg_frame_rate"
    `ffmpeg -i "$i" original_frames/%06d.png`
    """
    # TODO add downscaling option
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)  # Create outputFolder
    cmd = [definitions.FFMPEG_BIN,
           "-i", input_file,
           "-loglevel", "error",
           "-vsync", "cfr",
           os.path.join(output_folder, "%06d.png")]
    logging.info(" ".join(cmd))
    subprocess.run(cmd)


def encode_frames(input_folder, output_file, framerate):
    """Encode a folder of sequentially named frames into a video
    `ffmpeg -framerate 48 -i interpolated_frames/%06d.png -crf 18 output.mp4`
    """
    # TODO add an option for changing quality
    # TODO add progress bar for encoding
    pathlib.Path(os.path.dirname(output_file)).mkdir(parents=True, exist_ok=True)  # Create parent folder of outputFile
    cmd = [definitions.FFMPEG_BIN,
           "-framerate", str(framerate),
           "-i", os.path.join(input_folder, "%06d.png"),
           "-crf", "18",
           "-y", "-loglevel", "error",
           output_file]
    logging.info(" ".join(cmd))
    subprocess.run(cmd)
