"""
cain-ncnn-vulkan process wrapper

Cain does not support time-step (aka: always set to "0.5")
Neither does it support target-frames for the same reason
"""
# Built-in modules
import os
import pathlib
import shutil
import subprocess
# Local modules
import definitions
# External modules
from alive_progress import alive_bar

# Interpolation Defaults
DEFAULT_GPU_ID = "auto"
DEFAULT_THREADS = "1:1:1"


def interpolate_file_mode(input0_file, input1_file, output_file,
                          gpu_id=DEFAULT_GPU_ID, threads=DEFAULT_THREADS, **kwargs):
    """File-mode Interpolation"""
    # Make sure parent folder of output_file exists
    pathlib.Path(os.path.dirname(output_file)).mkdir(parents=True, exist_ok=True)
    cmd = [definitions.CAIN_NCNN_VULKAN_BIN,
           "-0", os.path.abspath(input0_file),
           "-1", os.path.abspath(input1_file),
           "-o", os.path.abspath(output_file),
           "-g", str(gpu_id),
           "-j", threads]
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=definitions.CAIN_NCNN_VULKAN_LOCATION)


def interpolate_folder_mode(input_folder, output_folder,
                            gpu_id=DEFAULT_GPU_ID, threads=DEFAULT_THREADS,
                            verbose=False, **kwargs):
    """Folder-mode Interpolation"""
    target_frames = len(os.listdir(input_folder)) * 2

    if os.path.isdir(output_folder):  # Delete output_folder if it exists to avoid conflicts
        shutil.rmtree(output_folder)
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)  # Create output_folder

    cmd = [definitions.CAIN_NCNN_VULKAN_BIN,
           "-i", os.path.abspath(input_folder),
           "-o", os.path.abspath(output_folder),
           "-g", str(gpu_id),
           "-j", threads,
           "-v"]
    if verbose is True:
        print(" ".join(cmd))
    # subprocess.run(cmd, cwd=definitions.CAIN_NCNN_VULKAN_LOCATION)
    with alive_bar(target_frames, enrich_print=False) as bar:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              cwd=definitions.CAIN_NCNN_VULKAN_LOCATION, bufsize=1, universal_newlines=True) as process:
            for line in process.stderr:
                if line.startswith("["):  # Starting GPU info
                    print(line, end="")
                elif line.endswith("done\n"):  # Verbose progress output
                    bar()
                elif line.startswith(("find_blob_index_by_name", "fopen")):  # Model not found error
                    raise OSError("Model not found: {}".format(line.replace("\n", "")))
                elif line.startswith("vkAllocateMemory failed"):  # VRAM memory error
                    raise RuntimeError("VRAM memory error: {}".format(line.replace("\n", "")))
                elif line.startswith(("vkWaitForFences failed", "vkQueueSubmit failed")):  # General vulkan error
                    raise RuntimeError("Vulkan error: {}".format(line.replace("\n", "")))
                else:
                    print(line, end="")
