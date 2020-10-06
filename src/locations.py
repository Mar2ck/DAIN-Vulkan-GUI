import logging
import os
from pathlib import Path
from platform import system
from shutil import which

# Project root folder
ROOT_DIR = os.path.dirname(__file__)

# Dain-ncnn-vulkan binary locations
DAIN_NCNN_VULKAN = {
    "Windows": os.path.join(ROOT_DIR, "dependencies", "dain-ncnn-vulkan", "dain-ncnn-vulkan.exe"),
    "Darwin": os.path.join(ROOT_DIR, "dependencies", "dain-ncnn-vulkan", "dain-ncnn-vulkan-macos"),
    "Linux": os.path.join(ROOT_DIR, "dependencies", "dain-ncnn-vulkan", "dain-ncnn-vulkan-ubuntu")
}
DAIN_NCNN_VULKAN_BIN = DAIN_NCNN_VULKAN[system()]
DAIN_NCNN_VULKAN_LOCATION = os.path.dirname(DAIN_NCNN_VULKAN_BIN)

# Cain-ncnn-vulkan binary locations
CAIN_NCNN_VULKAN = {
    "Windows": os.path.join(ROOT_DIR, "dependencies", "cain-ncnn-vulkan", "cain-ncnn-vulkan.exe"),
    "Darwin": os.path.join(ROOT_DIR, "dependencies", "cain-ncnn-vulkan", "cain-ncnn-vulkan-macos"),
    "Linux": os.path.join(ROOT_DIR, "dependencies", "cain-ncnn-vulkan", "cain-ncnn-vulkan-ubuntu")
}
CAIN_NCNN_VULKAN_BIN = CAIN_NCNN_VULKAN[system()]
CAIN_NCNN_VULKAN_LOCATION = Path(CAIN_NCNN_VULKAN_BIN).parent

# FFmpeg binary locations
FFMPEG = {
    "Windows": os.path.join(ROOT_DIR, "dependencies", "ffmpeg", "windows", "ffmpeg.exe"),
    "Darwin": os.path.join(ROOT_DIR, "dependencies", "ffmpeg", "macos", "ffmpeg"),
    "Linux": os.path.join(ROOT_DIR, "dependencies", "ffmpeg", "linux", "ffmpeg")
}
if os.path.isfile(FFMPEG[system()]) is True:  # Use bundled version first
    FFMPEG_BIN = FFMPEG[system()]
elif os.path.isfile(which("ffmpeg")) is True:  # Else use the system version
    FFMPEG_BIN = os.path.normpath(which("ffmpeg"))
else:
    FFMPEG_BIN = None
    logging.warning("ffmpeg not found")

# FFprobe binary locations
FFPROBE = {
    "Windows": os.path.join(ROOT_DIR, "dependencies", "ffmpeg", "windows", "ffprobe.exe"),
    "Darwin": os.path.join(ROOT_DIR, "dependencies", "ffmpeg", "macos", "ffprobe"),
    "Linux": os.path.join(ROOT_DIR, "dependencies", "ffmpeg", "linux", "ffprobe")
}
if os.path.isfile(FFPROBE[system()]) is True:  # Use bundled version first
    FFPROBE_BIN = FFPROBE[system()]
elif os.path.isfile(which("ffprobe")) is True:  # Else use the system version
    FFPROBE_BIN = os.path.normpath(which("ffprobe"))
else:
    FFPROBE_BIN = None
    logging.warning("ffprobe not found")

