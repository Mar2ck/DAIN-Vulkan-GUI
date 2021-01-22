"""
FFmpeg process wrapper
"""
# Built-in modules
# import logging
import os
import pathlib
import re
import subprocess
# Local modules
import definitions
import ffprobe
# External modules
from alive_progress import alive_bar


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
           os.path.join(output_folder, "%08d.png")]
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
        with alive_bar(frame_count, enrich_print=False) as bar:
            frame_count_processed_last = 0
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  bufsize=1, universal_newlines=True) as process:
                for line in process.stderr:
                    if line.startswith("frame="):
                        # Parses inbetween "frame=" and "fps="
                        frame_count_processed = int(re.findall(r"frame=(.+?)fps=", line)[0])
                        bar(incr=(frame_count_processed - frame_count_processed_last))
                        frame_count_processed_last = frame_count_processed
                    elif verbose is True:
                        print(line, end="")


def encode_frames(input_folder, output_file, framerate, verbose=False):
    """Encode a folder of sequentially named frames into a video
    `ffmpeg -framerate 48 -i interpolated_frames/%06d.png -crf 18 output.mp4`
    """
    # TODO add an option for changing quality
    frame_count = len(os.listdir(input_folder))
    pathlib.Path(os.path.dirname(output_file)).mkdir(parents=True, exist_ok=True)  # Create parent folder of outputFile
    cmd = [definitions.FFMPEG_BIN,
           "-framerate", str(framerate),
           "-i", os.path.join(input_folder, "%08d.png"),
           "-crf", "18",
           "-y",  # Always write file
           output_file]
    if verbose is True:
        print(" ".join(cmd))
    # subprocess.run(cmd)
    with alive_bar(frame_count, enrich_print=False) as bar:
        frame_count_processed_last = 0
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              bufsize=1, universal_newlines=True) as process:
            for line in process.stderr:
                if line.startswith("frame="):
                    # Parses inbetween "frame=" and "fps="
                    frame_count_processed = int(re.findall(r"frame=(.+?)fps=", line)[0])
                    bar(incr=(frame_count_processed - frame_count_processed_last))
                    frame_count_processed_last = frame_count_processed
                elif verbose is True:
                    print(line, end="")


def combine_video_audio(video_file, audio_file, output_file):
    # ffmpeg -i video.mp4 -i audio.webm -c:v copy -map 0:v:0 -map 1:a:0 output.mp4
    cmd = [definitions.FFMPEG_BIN,
           "-i", video_file,
           "-i", audio_file,
           "-c:v", "copy",  # Don't reencode video stream
           "-map", "0:v:0",
           "-map", "1:a:0",
           output_file]
    subprocess.run(cmd)
