#!/usr/bin/env python3
"""
Module for calculating the visual difference
between images via SSIM. This can be used to
detect whether video frames are duplicates.

Requires: pillow, SSIM-PIL, progress
Optional: pyopencl
"""
# Built-in modules
import os
import pathlib
# External modules
from PIL import Image
from SSIM_PIL import compare_ssim
from progress.bar import ShadyBar as progressBar


def calculate_ssim(image0_path, image1_path, use_gpu=True):
    """Calculates SSIM based on two images"""
    # print("Processing:", image0path)
    image0 = Image.open(image0_path)
    image1 = Image.open(image1_path)
    return compare_ssim(image0, image1, GPU=use_gpu)


def calculate_directory_ssim(directory_path, use_gpu=True, progress=False):
    """Calculates the SSIM for every image in a directory
    based on it and the image that precedes it
    """
    # print(os.path.abspath(directoryPath))
    directory_files = []
    for filePath in pathlib.Path(directory_path).glob('**/*'):  # List all files in the directory as their absolute path
        file_path_absolute = os.path.normpath(filePath.absolute())
        if file_path_absolute.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
            # Only adds files that have image extensions, fixes problems caused by "Thumbs.db"
            directory_files.append(file_path_absolute)
    directory_files.sort()
    # print(directory_files)
    directory_files_ssim = {}
    if progress is True:
        progress_bar_object = progressBar("Progress:", max=len(directory_files) - 1)
    for i in range(1, len(directory_files)):
        file_ssim = calculate_ssim(directory_files[i], directory_files[i - 1], use_gpu)
        # print(file_ssim)
        directory_files_ssim[directory_files[i]] = file_ssim
        if progress is True:
            progress_bar_object.next()
    if progress is True:
        progress_bar_object.finish()
    return directory_files_ssim


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-0", "--image0", help="Path of first image")
    parser.add_argument("-1", "--image1", help="Path of second image")
    parser.add_argument("-f", "--folder", help="Path of directory containing images")
    parser.add_argument("--disable-gpu", action="store_true",
                        help="Force SSIM calculation to use CPU instead of GPU")
    parser.add_argument("-p", "--progress", action="store_true",
                        help="Show progress bar when calculating a directory")
    args = vars(parser.parse_args())
    useGpu = not args["disable_gpu"]
    if not ((args["image0"] and args["image1"]) or args["folder"]):
        parser.error('Requires either both --image0 and --image1 or --folder')

    if (args["image0"] is not None) and (args["image1"] is not None):  # -image0 and -image1
        SSIM = calculate_ssim(args["image0"], args["image1"], useGpu)
        print("SSIM: {}".format(SSIM))
    elif args["folder"] is not None:  # -folder
        directorySSIM = calculate_directory_ssim(args["folder"], useGpu, args["progress"])
        for file in sorted(directorySSIM.keys()):
            print("{}: {}".format(file, directorySSIM[file]))
