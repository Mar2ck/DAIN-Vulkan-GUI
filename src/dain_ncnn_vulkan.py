"""
dain-ncnn-vulkan process wrapper
"""
# Built-in modules
# import logging
import os
import pathlib
import subprocess
# Local modules
import definitions
# External modules
from progress.bar import ShadyBar as progressBar

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
           "-g", str(gpu_id),
           "-j", threads]
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=definitions.DAIN_NCNN_VULKAN_LOCATION)


def interpolate_folder_mode(input_folder, output_folder, multiplier=DEFAULT_MULTIPLIER,
                            tile_size=DEFAULT_TILE_SIZE, gpu_id=DEFAULT_GPU_ID, threads=DEFAULT_THREADS,
                            verbose=False):
    """Folder-mode Interpolation"""
    # Calculate double input frames as default
    target_frames = len(os.listdir(input_folder)) * int(multiplier)
    # Make sure output_folder exists
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)
    cmd = [definitions.DAIN_NCNN_VULKAN_BIN,
           "-i", os.path.abspath(input_folder),
           "-o", os.path.abspath(output_folder),
           "-n", str(target_frames),
           "-t", str(tile_size),
           "-g", str(gpu_id),
           "-j", threads,
           "-v"]
    if verbose is True:
        print(" ".join(cmd))
    # subprocess.run(cmd, cwd=definitions.DAIN_NCNN_VULKAN_LOCATION)
    progress_bar_created = False
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          cwd=definitions.DAIN_NCNN_VULKAN_LOCATION, bufsize=1, universal_newlines=True) as process:
        for line in process.stderr:
            if line.startswith("["):  # Starting GPU info
                print(line, end="")
            elif line.endswith("done\n"):  # Verbose progress output
                if progress_bar_created is False:
                    progress_bar_object = progressBar("Progress:", max=target_frames)
                    progress_bar_created = True
                progress_bar_object.next()
            elif line.startswith("invalid tilesize argument"):  # Tilesize error
                raise ValueError(line.replace("\n", ""))
            elif line.startswith(("find_blob_index_by_name", "fopen")):  # Model not found error
                raise OSError("Model not found: {}".format(line.replace("\n", "")))
            elif line.startswith("vkAllocateMemory failed"):  # VRAM memory error
                raise RuntimeError("VRAM memory error: {}".format(line.replace("\n", "")))
            elif line.startswith(("vkWaitForFences failed", "vkQueueSubmit failed")):  # General vulkan error
                raise RuntimeError("Vulkan error: {}".format(line.replace("\n", "")))
            else:
                print(line, end="")
    progress_bar_object.finish()
