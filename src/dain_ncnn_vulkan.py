"""
dain-ncnn-vulkan process wrapper
"""
# Built-in modules
import logging
import os
import pathlib
import subprocess
# Local modules
import definitions

# Interpolation Defaults
DEFAULT_TIME_STEP = 0.5
DEFAULT_MULTIPLIER = 2
DEFAULT_TILE_SIZE = 256
DEFAULT_GPU_ID = "auto"
DEFAULT_THREADS = "1:1:1"


def interpolate_file_mode(input0_file, input1_file, output_file, time_step=DEFAULT_TIME_STEP,
                          tile_size=DEFAULT_TILE_SIZE, gpu_id=DEFAULT_GPU_ID, threads=DEFAULT_THREADS):
    """File-mode Interpolation"""
    # Make sure parent folder of output_file exists
    pathlib.Path(os.path.dirname(output_file)).mkdir(parents=True, exist_ok=True)
    cmd = [definitions.DAIN_NCNN_VULKAN_BIN,
           "-0", os.path.abspath(input0_file),
           "-1", os.path.abspath(input1_file),
           "-o", os.path.abspath(output_file),
           "-s", str(time_step),
           "-t", str(tile_size),
           "-g", gpu_id,
           "-j", threads]
    logging.info(" ".join(cmd))
    subprocess.run(cmd, cwd=definitions.DAIN_NCNN_VULKAN_LOCATION)


def interpolate_folder_mode(input_folder, output_folder, multiplier=DEFAULT_MULTIPLIER,
                            tile_size=DEFAULT_TILE_SIZE, gpu_id=DEFAULT_GPU_ID, threads=DEFAULT_THREADS):
    """Folder-mode Interpolation"""
    # Calculate double input frames as default
    target_frames = str(len(os.listdir(input_folder)) * int(multiplier))
    # Make sure output_folder exists
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)
    cmd = [definitions.DAIN_NCNN_VULKAN_BIN,
           "-i", os.path.abspath(input_folder),
           "-o", os.path.abspath(output_folder),
           "-n", str(target_frames),
           "-t", str(tile_size),
           "-g", gpu_id,
           "-j", threads]
    logging.info(" ".join(cmd))
    subprocess.run(cmd, cwd=definitions.DAIN_NCNN_VULKAN_LOCATION)
