"""
Module for handling video frame extraction (aka: "step 1")
"""
# Built-in modules
import os
import pathlib
# External modules
from PIL import Image


def png_remove_alpha_channel(file_path):
    png = Image.open(file_path).convert("RGBA")
    background = Image.new("RGBA", png.size, (255, 255, 255))  # White background created
    alpha_composite = Image.alpha_composite(background, png)  # Transparent png put on background
    alpha_composite.convert("RGB").save(file_path)


def png_directory_remove_alpha_channel(directory_path):
    """Converts all .png files in a folder to be alpha-less"""
    for i in pathlib.Path(directory_path).glob('**/*.png'):
        png_remove_alpha_channel(i.absolute())
