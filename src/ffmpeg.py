"""
FFmpeg process wrapper
"""
# Built-in modules
import logging
import os
import pathlib
import subprocess
# Local modules
import locations


def extract_frames(input_file, output_folder):  # "Step 1"
    # ffmpeg -i "$i" original_frames/%06d.png
    """Extract video frames to a folder
    for -vsync: "crf" will use "r_frame_rate", "vfr" will use "avg_frame_rate"
    """
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)  # Create outputFolder
    cmd = [locations.FFMPEG_BIN,
           "-i", input_file,
           "-loglevel", "error",
           "-vsync", "cfr",
           os.path.join(output_folder, "%06d.png")]
    logging.info(" ".join(cmd))
    subprocess.run(cmd)


def encode_frames(input_folder, output_file, framerate):
    # ffmpeg -framerate 48 -i interpolated_frames/%06d.png output.mp4
    """Encode a folder of sequentially named frames into a video"""
    pathlib.Path(os.path.dirname(output_file)).mkdir(parents=True, exist_ok=True)  # Create parent folder of outputFile
    cmd = [locations.FFMPEG_BIN,
           "-framerate", str(framerate),
           "-i", os.path.join(input_folder, "%06d.png"),
           "-crf", "18",
           "-y", "-loglevel", "error",
           output_file]
    logging.info(" ".join(cmd))
    subprocess.run(cmd)
