"""
Module for handling interpolation (aka: "step 2")
"""
# Built-in Modules
import os
import pathlib
import shutil
# Local Modules
import dain_ncnn_vulkan
import cain_ncnn_vulkan

DEFAULT_MULTIPLIER = 2
DEFAULT_MULTIPLIER_DYNAMIC = 1
DEFAULT_INTERPOLATOR = "dain-ncnn"


def _make_duplicate_frames(input_file, output_folder, output_count):
    """
    Copies the input_file a number of time
    Useful for creating duplicate frames before a scene change or at the end of a non-looping video
    """
    inputFileNumber = int(pathlib.Path(input_file).stem)  # Get Filename (without extension) from path
    for i in range(output_count):
        outputFile = "{:06d}.png".format(inputFileNumber + i + 1)
        args = [os.path.join(output_folder, input_file), os.path.join(output_folder, outputFile)]
        print("Duplicating:", " -> ".join(args))
        shutil.copyfile(*args)


def cain_folder_multiplier_handler(input_folder, output_folder, multiplier, **kwargs):
    """
    Achieve interpolation past 2x without using target_frames (which cain lacks)
    by interpolating from one folder to the next Eg. First (1x -> 2x) then (2x -> 4x)
    Multiplies to a power of 2
    """
    folderParent = pathlib.Path(output_folder).parent
    multiplierInternal = 1
    cainFolderFrom = input_folder
    cainFolderTo = None
    if not (multiplier > 1):
        raise ValueError("Multiplier must be higher than 1")
    else:
        if not ((multiplier & (multiplier - 1) == 0) and multiplier != 0):  # Check if not a power of 2
            raise ValueError("Multiplier must be a power of 2 (2, 4, 8, etc.)")
        else:
            cainOutputFolders = []
            while multiplierInternal < multiplier:
                multiplierInternal = multiplierInternal * 2
                print("From: \"{}\"".format(cainFolderFrom))
                cainFolderTo = os.path.join(folderParent, ("cain-" + str(multiplierInternal) + "x"))
                cainOutputFolders.append(cainFolderTo)
                print("To: \"{}\"".format(cainFolderTo))

                cain_ncnn_vulkan.interpolate_folder_mode(cainFolderFrom, cainFolderTo, **kwargs)
                cainFolderFrom = cainFolderTo  # Set last output folder to the input folder for the next loop
            print("Renaming \"{}\" to \"{}\"".format(cainFolderTo, output_folder))
            if os.path.isdir(output_folder) is True:
                print("\"{}\" already exists, deleting".format(output_folder))
                shutil.rmtree(output_folder)
            os.rename(cainFolderTo, output_folder)
            if cainOutputFolders[:-1]:
                print("Deleting leftover folders:", cainOutputFolders[:-1])
                for folder in cainOutputFolders[:-1]:
                    shutil.rmtree(folder)


def interpolate_static(input_folder, output_folder,
                       mulitplier=DEFAULT_MULTIPLIER, interpolator=None, loop=False, **kwargs):
    """
    Creates a static number of new frames between the original frames
    Eg: 2x = 1 original, 1 interpolated; 3x = 1 original, 2 interpolated
    """
    pass


def interpolate_dynamic(input_folder, output_folder, original_frame_count, loop=False, **kwargs):
    """
    Creates a dynamic number of new frames that depends on the length of time between each original frame
    Reads frame position from original file names so removed frames are replaced
    Example at 2x: 1.png -> 2.png, 1 interpolated frame inbetween; 1.png -> 3.png, 3 interpolated frames inbetween
    ((gap_frames + 1) * multiplier) - 1 = interpolated_frames
    """
    def dynamic_internal(image0_filename, image1_filename, custom_frame_difference=None):
        shutil.copyfile(os.path.join(input_folder, image0_filename),os.path.join(output_folder, image0_filename))
        image0Number = int(image0_filename.split(".")[0])
        image1Number = int(image1_filename.split(".")[0])
        print("Image0: {}".format(image0_filename))
        print("Image1: {}".format(image1_filename))
        frameDifference = (image1Number - image0Number) if custom_frame_difference is None else custom_frame_difference
        inbetweenFrames = frameDifference - 1
        print("Inbetween frames: {}".format(inbetweenFrames))
        if inbetweenFrames >= 1:
            for n in range(inbetweenFrames):
                interpolatedFrameNumber = image0Number + n + 1
                interpolatedFrameName = "{:06d}.png".format(interpolatedFrameNumber)
                interpolatedFrameTimeStep = (n + 1) / frameDifference
                print("Interpolated frame: {} at time-step {}".format(interpolatedFrameName, interpolatedFrameTimeStep))
                dain_ncnn_vulkan.interpolate_file_mode(os.path.join(input_folder, image0_filename),
                                                       os.path.join(input_folder, image1_filename),
                                                       os.path.join(output_folder, interpolatedFrameName),
                                                       time_step=interpolatedFrameTimeStep,
                                                       **kwargs)
        print("")

    # Run against all frames except last
    inputFolderFiles = sorted(os.listdir(input_folder))
    for i in range(len(inputFolderFiles)-1):
        dynamic_internal(inputFolderFiles[i], inputFolderFiles[i+1])

    # Last frame handling
    frameDifferenceToEnd = (original_frame_count - int(inputFolderFiles[-1].split(".")[0]) + 1)
    if loop is True:  # image1 is first frame
        dynamic_internal(inputFolderFiles[-1], inputFolderFiles[0],
                         custom_frame_difference=frameDifferenceToEnd)
    else:  # create duplicates til original frame count met
        shutil.copyfile(os.path.join(input_folder, inputFolderFiles[-1]),
                        os.path.join(output_folder, inputFolderFiles[-1]))
        _make_duplicate_frames(os.path.join(input_folder, inputFolderFiles[-1]), output_folder,
                               (frameDifferenceToEnd - 1))
