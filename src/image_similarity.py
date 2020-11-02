#!/usr/bin/env python3
"""
Module for calculating the visual difference
between images via SSIM. This can be used to
detect whether video frames are duplicates.

Requires: pillow, SSIM-PIL, progress
Optional: pyopencl
"""
# Built-in modules
import logging
import os
import pathlib
# External modules
from PIL import Image
from SSIM_PIL import compare_ssim
from alive_progress import alive_bar

DEFAULT_USE_GPU = True
DEFAULT_SHOW_PROGRESS = False


def calculate_ssim(image0_path, image1_path, use_gpu=True, resize_before_comparison=False):
    """Calculates SSIM based on two images"""
    # print("Processing:", image0path)
    image0 = Image.open(image0_path)
    image1 = Image.open(image1_path)
    if resize_before_comparison is True:
        image0 = image0.resize((512, 512))
        image1 = image1.resize((512, 512))
    return compare_ssim(image0, image1, GPU=use_gpu)


def calculate_directory_ssim(directory_path, **kwargs):
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
    with alive_bar(len(directory_files) - 1, enrich_print=False) as bar:
        for i in range(1, len(directory_files)):
            file_ssim = calculate_ssim(directory_files[i], directory_files[i - 1], **kwargs)
            # print(file_ssim)
            directory_files_ssim[directory_files[i]] = file_ssim
            bar()
    return directory_files_ssim


def delete_similar_images(directory_path, threshold, **kwargs):
    """Deletes any image that has an SSIM higher then the specified threshold"""
    ssimResults = calculate_directory_ssim(directory_path, **kwargs)
    for ssimResultsFile in sorted(ssimResults.keys()):
        if ssimResults[ssimResultsFile] > float(threshold):
            logging.info("Removing: {}".format(ssimResultsFile))
            os.remove(ssimResultsFile)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-0", "--image0", help="Path of first image")
    parser.add_argument("-1", "--image1", help="Path of second image")
    parser.add_argument("-f", "--folder", help="Path of directory containing images")
    parser.add_argument("--delete-threshold", type=float, help="If specified, deletes duplicate images automatically"
                                                               " based on a similarity percentage (Eg. 0.95)")
    parser.add_argument("--disable-gpu", action="store_true", help="Force SSIM calculation to use CPU instead of GPU")
    args = vars(parser.parse_args())
    useGpu = not args["disable_gpu"]
    if not ((args["image0"] and args["image1"]) or args["folder"]):
        parser.error('Requires either both --image0 and --image1 or --folder')

    if (args["image0"] is not None) and (args["image1"] is not None):  # -image0 and -image1
        SSIM = calculate_ssim(args["image0"], args["image1"], use_gpu=useGpu)
        print("SSIM: {}".format(SSIM)) # -folder delete mode
    elif (args["folder"] is not None) and (args["delete_threshold"] is not None):
        delete_similar_images(args["folder"], args["delete_threshold"], use_gpu=useGpu)
    elif args["folder"] is not None:  # -folder
        directorySSIM = calculate_directory_ssim(args["folder"], use_gpu=useGpu)
        for file in sorted(directorySSIM.keys()):
            print("{}: {}".format(file, directorySSIM[file]))
