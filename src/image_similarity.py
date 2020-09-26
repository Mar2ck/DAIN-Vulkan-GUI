#!/usr/bin/env python3
"""
This file contains functions for calculating the
visual difference between images via SSIM. This
can be used to detect whether video frames
are duplicates.

https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.structural_similarity

Requires: opencv-python, scikit-image, progress
"""
# Built-in modules
import os
# External modules
import cv2
from skimage.metrics import structural_similarity
from progress.bar import ShadyBar


def CalculateSSIM(image0path, image1path, multichannel=False):
    """Calculates SSIM based on two images"""
    image0 = cv2.imread(image0path)
    image1 = cv2.imread(image1path)
    if multichannel is True:
        # Calculating using RGB instead of gray is slower but probably more accurate
        return structural_similarity(image0, image1, multichannel=True)
    else:
        # Convert to gray first for ~2.5x speed increase
        gray0 = cv2.cvtColor(image0, cv2.COLOR_BGR2GRAY)
        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        return structural_similarity(gray0, gray1)


def CalculateDirectorySSIM(directoryPath, multichannel=False, progress=False):
    """Calculates the SSIM for every image in a directory
    based on it and the image that proceeds it
    """
    # print(os.path.abspath(directoryPath))
    directoryFiles = sorted(os.listdir(directoryPath))
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
    parser.add_argument("-m", "--multichannel", action="store_true",
                        help="Calculate RGB channels on their own instead of combining into greyscale")
    parser.add_argument("-p", "--progress", action="store_true",
                        help="Show progress bar when calculating a directory")
    args = vars(parser.parse_args())

    if (args["image0"] is not None) and (args["image1"] is not None):  # -image0 and -image1
        SSIM = CalculateSSIM(args["image0"], args["image1"], args["multichannel"])
        print("SSIM: {}".format(SSIM))
    elif args["folder"] is not None:  # -folder
        directorySSIM = CalculateDirectorySSIM(args["folder"], args["multichannel"], args["progress"])
        print(directorySSIM)
