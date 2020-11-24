import logging
import os
from pathlib import Path
from platform import system
from shutil import which

# Project root folder
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# Default parameters
DEFAULT_FRAME_MULTIPLIER = 2
DEFAULT_INTERPOLATOR_MODE = "static"
DEFAULT_INTERPOLATOR_ENGINE = "dain-ncnn"
DEFAULT_LOOP = False
DEFAULT_VIDEO_TYPE = "mp4"

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

# Rife-ncnn-vulkan binary locations
RIFE_NCNN_VULKAN = {
    "Windows": os.path.join(ROOT_DIR, "dependencies", "rife-ncnn-vulkan", "rife-ncnn-vulkan.exe"),
    "Darwin": os.path.join(ROOT_DIR, "dependencies", "rife-ncnn-vulkan", "rife-ncnn-vulkan-macos"),
    "Linux": os.path.join(ROOT_DIR, "dependencies", "rife-ncnn-vulkan", "rife-ncnn-vulkan-ubuntu")
}
RIFE_NCNN_VULKAN_BIN = RIFE_NCNN_VULKAN[system()]
RIFE_NCNN_VULKAN_LOCATION = Path(RIFE_NCNN_VULKAN_BIN).parent

# FFmpeg binary locations
FFMPEG = {
    "Windows": os.path.join(ROOT_DIR, "dependencies", "ffmpeg", "windows", "ffmpeg.exe"),
    "Darwin": os.path.join(ROOT_DIR, "dependencies", "ffmpeg", "macos", "ffmpeg"),
    "Linux": os.path.join(ROOT_DIR, "dependencies", "ffmpeg", "linux", "ffmpeg")
}
FFMPEG_BIN = None
if os.path.isfile(FFMPEG[system()]) is True:  # Use bundled version first
    logging.debug("FFmpeg version: bundled")
    FFMPEG_BIN = FFMPEG[system()]
elif os.path.isfile(which("ffmpeg")) is True:  # Else use the system version
    logging.debug("FFmpeg version: system")
    FFMPEG_BIN = os.path.normpath(which("ffmpeg"))
else:
    logging.warning("ffmpeg not found")

# FFprobe binary locations
FFPROBE = {
    "Windows": os.path.join(ROOT_DIR, "dependencies", "ffmpeg", "windows", "ffprobe.exe"),
    "Darwin": os.path.join(ROOT_DIR, "dependencies", "ffmpeg", "macos", "ffprobe"),
    "Linux": os.path.join(ROOT_DIR, "dependencies", "ffmpeg", "linux", "ffprobe")
}
FFPROBE_BIN = None
if os.path.isfile(FFPROBE[system()]) is True:  # Use bundled version first
    logging.debug("FFprobe version: bundled")
    FFPROBE_BIN = FFPROBE[system()]
elif os.path.isfile(which("ffprobe")) is True:  # Else use the system version
    logging.debug("FFprobe version: system")
    FFPROBE_BIN = os.path.normpath(which("ffprobe"))
else:
    logging.warning("ffprobe not found")

# RIFE Model location
RIFE_MODEL = os.path.join(ROOT_DIR, "RIFE", "train_log")
