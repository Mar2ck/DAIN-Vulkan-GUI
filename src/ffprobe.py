"""
FFprobe process wrapper

 - Some videos don't return "duration" and "nb_frames" such as apng
 - "nb_read_frames" won't be accurate if the input video is vfr

http://svn.ffmpeg.org/doxygen/trunk/structAVStream.html
"avg_frame_rate" is "Average framerate" aka: duration/framecount
"r_frame_rate" is "Real base framerate" which is the lowest common framerate of all frames in the video
"""
# Built-in modules
import json
import logging
import subprocess
# Local modules
import locations


def analyze_video_stream_metadata(inputFile):
    """Analyzes a video's stream and returns it's properties"""
    # ffprobe -show_streams -select_streams v:0 -print_format json -loglevel quiet input.mp4
    cmd = [locations.FFPROBE_BIN,
           "-show_streams",
           "-select_streams", "v:0",
           "-print_format", "json",
           "-loglevel", "quiet",
           inputFile]
    logging.info(" ".join(cmd))
    output = subprocess.check_output(cmd, universal_newlines=True)
    parsedOutput = json.loads(output)["streams"][0]
    return({
        "width": parsedOutput["width"],
        "height": parsedOutput["height"],
        "fpsReal": parsedOutput["r_frame_rate"],
        "fpsAverage": parsedOutput["avg_frame_rate"]
    })


def analyze_video_frame_metadata(inputFile):
    """Analyzes a video's frames and returns an array with their individual properities"""
    # ffprobe -show_frames -select_streams v:0 -print_format json -loglevel quiet input.mp4
    cmd = [locations.FFPROBE_BIN,
           "-show_frames",
           "-select_streams", "v:0",
           "-print_format", "json",
           "-loglevel", "quiet",
           inputFile]
    logging.info(" ".join(cmd))
    output = subprocess.check_output(cmd, universal_newlines=True)
    parsedOutput = json.loads(output)["packets"]
    return parsedOutput
