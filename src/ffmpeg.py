"""
FFmpeg process wrapper
"""
# Built-in modules
import logging
import os
import pathlib
import re
import subprocess
# Local modules
import definitions
import ffprobe
# External modules
from progress.bar import ShadyBar as progressBar


def extract_frames(input_file, output_folder, verbose=False):
    """Extract video frames to a folder
    for -vsync: "crf" will use "r_frame_rate", "vfr" will use "avg_frame_rate"
    `ffmpeg -i "$i" original_frames/%06d.png`
    """
    # TODO add downscaling option

    stream_metadata = ffprobe.analyze_video_stream_metadata(input_file)
    frame_count = int(stream_metadata["packetCount"])
    vfrBool = (stream_metadata["fpsReal"] != stream_metadata["fpsAverage"])  # Video is cfr when average fps = real fps

    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)  # Create outputFolder
    cmd = [definitions.FFMPEG_BIN,
           "-i", input_file,
           "-vsync", "cfr",
           "-pix_fmt", "rgb24",  # Usually defaults to rgba which causes alpha problems
           os.path.join(output_folder, "%06d.png")]
    if verbose is True:
        print(" ".join(cmd))
    # subprocess.run(cmd)
    if vfrBool is True:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              bufsize=1, universal_newlines=True) as process:
            for line in process.stderr:
                if line.startswith("frame="):
                    print(line, end="")
    else:
        progress_bar_object = progressBar("Progress:", max=frame_count)
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              bufsize=1, universal_newlines=True) as process:
            for line in process.stderr:
                if line.startswith("frame="):
                    frame_count = int(re.findall(r"frame=(.+?)fps=", line)[0])  # Parses inbetween "frame=" and "fps="
                    progress_bar_object.goto(frame_count)
        progress_bar_object.finish()


def encode_frames(input_folder, output_file, framerate, verbose=False):
    """Encode a folder of sequentially named frames into a video
    `ffmpeg -framerate 48 -i interpolated_frames/%06d.png -crf 18 output.mp4`
    """
    # TODO add an option for changing quality
    # TODO add audio passthrough from the source video
    frames_count = len(os.listdir(input_folder))
    pathlib.Path(os.path.dirname(output_file)).mkdir(parents=True, exist_ok=True)  # Create parent folder of outputFile
    cmd = [definitions.FFMPEG_BIN,
           "-framerate", str(framerate),
           "-i", os.path.join(input_folder, "%06d.png"),
           "-crf", "18",
           "-y",  # Always write file
           output_file]
    if verbose is True:
        print(" ".join(cmd))
    # subprocess.run(cmd)
    progress_bar_object = progressBar("Progress:", max=frames_count)
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          bufsize=1, universal_newlines=True) as process:
        for line in process.stderr:
            if line.startswith("frame="):
                frame_count = int(re.findall(r"frame=(.+?)fps=", line)[0])  # Finds number between "frame=" and "fps="
                progress_bar_object.goto(frame_count)
            else:
                print(line, end="")
    progress_bar_object.finish()
