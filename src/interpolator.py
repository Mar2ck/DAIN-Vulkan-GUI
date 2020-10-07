"""
Module for handling interpolation (aka: "step 2")
"""
# Local Modules
import dain_ncnn_vulkan
import cain_ncnn_vulkan


def _make_duplicate_frames(input_file, multiplier=None):
    """
    Copies the input_file to the output_file
    Useful for creating duplicate frames before a scene change or at the end of a non-looping video
    Eg: 2x = 1 duplicate, 3x = 2 duplicates
    """
    pass


def interpolate_static(input_folder, output_folder, mulitplier=None, perfect_loop=False):
    """
    Creates a static number of new frames between the original frames
    Eg: 2x = 1 original, 1 interpolated; 3x = 1 original, 2 interpolated
    """
    pass


def interpolate_dynamic(input_folder, output_folder, mulitplier=None, perfect_loop=False):
    """
    Creates a dynamic number of new frames that depends on the length of time between each original frame
    Reads frame position from original file names so removed frames are replaced
    Example at 2x: 1.png -> 2.png, 1 interpolated frame inbetween; 1.png -> 3.png, 3 interpolated frames inbetween
    ((gap_frames + 1) * multiplier) - 1 = interpolated_frames
    """
    pass
