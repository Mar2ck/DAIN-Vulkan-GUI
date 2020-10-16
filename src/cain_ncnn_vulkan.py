"""
cain-ncnn-vulkan process wrapper

Cain does not support time-step (aka: always set to "0.5")
Neither does it support target-frames for the same reason
"""
# Built-in modules
import logging
import os
import pathlib
import subprocess
# Local modules
import definitions

# Interpolation Defaults
DEFAULT_TILE_SIZE = 512
DEFAULT_GPU_ID = "auto"
DEFAULT_THREADS = "1:1:1"


def interpolate_file_mode(input0_file, input1_file, output_file,
                          tile_size=DEFAULT_TILE_SIZE, gpu_id=DEFAULT_GPU_ID, threads=DEFAULT_THREADS):
    """File-mode Interpolation"""
    # Make sure parent folder of output_file exists
    pathlib.Path(os.path.dirname(output_file)).mkdir(parents=True, exist_ok=True)
    cmd = [definitions.CAIN_NCNN_VULKAN_BIN,
           "-0", os.path.abspath(input0_file),
           "-1", os.path.abspath(input1_file),
           "-o", os.path.abspath(output_file),
           "-t", str(tile_size),
           "-g", gpu_id,
           "-j", threads]
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=definitions.CAIN_NCNN_VULKAN_LOCATION)


def interpolate_folder_mode(input_folder, output_folder,
                            tile_size=DEFAULT_TILE_SIZE, gpu_id=DEFAULT_GPU_ID, threads=DEFAULT_THREADS,
                            verbose=True):
    """Folder-mode Interpolation"""
    # Make sure output_folder exists
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)
    cmd = [definitions.CAIN_NCNN_VULKAN_BIN,
           "-i", os.path.abspath(input_folder),
           "-o", os.path.abspath(output_folder),
           "-t", str(tile_size),
           "-g", gpu_id,
           "-j", threads]
    if verbose is True:
        cmd.append("-v")
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=definitions.CAIN_NCNN_VULKAN_LOCATION)
