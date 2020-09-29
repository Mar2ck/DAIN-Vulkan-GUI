#!/usr/bin/env python3
"""
This file contains functions for calculating the
visual difference between images via SSIM. This
can be used to detect whether video frames
are duplicates.

https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.structural_similarity

Requires: opencv-python-headless, scikit-image, progress
"""
# Built-in modules
import os
import pathlib
# External modules
import cv2
from skimage.metrics import structural_similarity
from progress.bar import ShadyBar


def CalculateSSIM(image0path, image1path, multichannel=False, resize=512): # resize=None disables resizing
    """Calculates SSIM based on two images"""
    # print("Processing:", image0path)
    image0 = cv2.imread(image0path)
    image1 = cv2.imread(image1path)
    # In OpenCV width = 1 and height = 0
    # if resize is not None:
    #     if image0.shape[1] > resize:
    #         imageWidth

    if multichannel is True:
        # Calculating using RGB instead of gray is slower but probably more accurate
        return structural_similarity(image0, image1, multichannel=True)
    else:
        # Convert to gray first for ~2.5x speed increase
        return structural_similarity(cv2.cvtColor(image0, cv2.COLOR_BGR2GRAY),
                                     cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY))


def CalculateDirectorySSIM(directoryPath, multichannel=False, progress=False):
    """Calculates the SSIM for every image in a directory
    based on it and the image that precedes it
    """
    # print(os.path.abspath(directoryPath))
    directoryFiles = []
    for filePath in pathlib.Path(directoryPath).glob('**/*'): # List all files in the directory as their absolute path
        filePathAbsolute = os.path.normpath(filePath.absolute())
        if filePathAbsolute.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')): # Only adds files that have image extensions, fixes problems caused by "Thumbs.db"
            directoryFiles.append(filePathAbsolute)
    directoryFiles.sort()
    # print(directoryFiles)
    directoryFilesSSIM = {}
    if progress is True: progressBar = ShadyBar("Progress:", max=len(directoryFiles) - 1)
    for i in range(1, len(directoryFiles)):
        fileSSIM = CalculateSSIM(directoryFiles[i], directoryFiles[i - 1], multichannel)
        # print(fileSSIM)
        directoryFilesSSIM[directoryFiles[i]] = fileSSIM
        if progress is True: progressBar.next()
    if progress is True: progressBar.finish()
    return directoryFilesSSIM


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-0", "--image0", help="Path of first image")
    parser.add_argument("-1", "--image1", help="Path of second image")
    parser.add_argument("-f", "--folder", help="Path of directory containing images")
    parser.add_argument("--multichannel", action="store_true",
                        help="Calculate RGB channels on their own instead of combining into greyscale")
    parser.add_argument("-p", "--progress", action="store_true",
                        help="Show progress bar when calculating a directory")
    args = vars(parser.parse_args())

    if not ((args["image0"] and args["image1"]) or args["folder"]):
        parser.error('Requires --image0 and --image1 or --folder')

    if (args["image0"] is not None) and (args["image1"] is not None):  # -image0 and -image1
        SSIM = CalculateSSIM(args["image0"], args["image1"], args["multichannel"])
        print("SSIM: {}".format(SSIM))
    elif args["folder"] is not None:  # -folder
        directorySSIM = CalculateDirectorySSIM(args["folder"], args["multichannel"], args["progress"])
        for i in sorted(directorySSIM.keys()):
            print("{}: {}".format(i, directorySSIM[i]))
