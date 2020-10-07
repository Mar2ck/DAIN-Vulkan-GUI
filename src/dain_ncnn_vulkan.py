"""
dain-ncnn-vulkan process wrapper
"""
# Built-in modules
import logging
import os
import pathlib
import subprocess
# Local modules
import locations

# Interpolation Defaults
DEFAULT_TIME_STEP = "0.5"
DEFAULT_MULTIPLIER = 2
DEFAULT_TILESIZE = "256"
DEFAULT_GPUID = "auto"
DEFAULT_THREADS = "1:1:1"


def interpolate_file_mode(input0_file, input1_file, output_file,
                          time_step=None, tile_size=None, gpuid=None, threads=None):
    """File-mode Interpolation"""
    # Make sure parent folder of output_file exists
    pathlib.Path(os.path.dirname(output_file)).mkdir(parents=True, exist_ok=True)
    cmd = [locations.DAIN_NCNN_VULKAN_BIN,
           "-0", os.path.abspath(input0_file),
           "-1", os.path.abspath(input1_file),
           "-o", os.path.abspath(output_file),
           "-s", (DEFAULT_TIME_STEP if time_step is None else time_step),
           "-t", (DEFAULT_TILESIZE if tile_size is None else tile_size),
           "-g", (DEFAULT_GPUID if gpuid is None else gpuid),
           "-j", (DEFAULT_THREADS if threads is None else threads)]
    logging.info(" ".join(cmd))
    subprocess.run(cmd, cwd=locations.DAIN_NCNN_VULKAN_LOCATION)


def interpolate_folder_mode(input_folder, output_folder,
                            multiplier=None, tile_size=None, gpuid=None, threads=None):
    """Folder-mode Interpolation"""
    # Calculate double input frames as default
    target_frames = str(len(os.listdir(input_folder) * (DEFAULT_MULTIPLIER if multiplier is None else int(multiplier))))
    # Make sure output_folder exists
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)
    cmd = [locations.DAIN_NCNN_VULKAN_BIN,
           "-i", os.path.abspath(input_folder),
           "-o", os.path.abspath(output_folder),
           "-n", target_frames,
           "-t", (DEFAULT_TILESIZE if tile_size is None else tile_size),
           "-g", (DEFAULT_GPUID if gpuid is None else gpuid),
           "-j", (DEFAULT_THREADS if threads is None else threads)]
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=locations.DAIN_NCNN_VULKAN_LOCATION)
