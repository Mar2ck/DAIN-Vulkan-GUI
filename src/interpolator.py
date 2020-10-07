"""
Module for handling interpolation (aka: "step 2")
"""
# Built-in Modules
import os
import pathlib
import shutil
# Local Modules
# import dain_ncnn_vulkan
import cain_ncnn_vulkan

DEFAULT_MULTIPLIER = 2
DEFAULT_INTERPOLATOR = "dain-ncnn"


def _make_duplicate_frames(input_file, multiplier=None):
    """
    Copies the input_file to the output_file
    Useful for creating duplicate frames before a scene change or at the end of a non-looping video
    Eg: 2x = 1 duplicate, 3x = 2 duplicates
    """
    pass


def cain_folder_multiplier_handler(input_folder, output_folder, multiplier, **kwargs):
    """
    kwargs are passed through to the interpolator process

    Unlike dain-ncnn, cain-ncnn can't multiply frames by an arbitrary amount.
    This is circuvented by running it multiple times from the last folder to the next.
    Eg. First (1x -> 2x) then (2x -> 4x)
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
                print("Interpolating to:", str(multiplierInternal) + "x")

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


def interpolate_static(input_folder, output_folder, mulitplier=None, interpolator=None, perfect_loop=False):
    """
    Creates a static number of new frames between the original frames
    Eg: 2x = 1 original, 1 interpolated; 3x = 1 original, 2 interpolated
    """
    pass


def interpolate_dynamic(input_folder, output_folder, mulitplier=None, interpolator=None, perfect_loop=False):
    """
    Creates a dynamic number of new frames that depends on the length of time between each original frame
    Reads frame position from original file names so removed frames are replaced
    Example at 2x: 1.png -> 2.png, 1 interpolated frame inbetween; 1.png -> 3.png, 3 interpolated frames inbetween
    ((gap_frames + 1) * multiplier) - 1 = interpolated_frames
    """
    pass
