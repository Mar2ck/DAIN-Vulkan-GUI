"""
RIFE PyTorch implementation
"""
# Built-in modules
# import numpy
import os
import pathlib
import shutil
import sys
import warnings
# Local modules
import definitions
import RIFE.model.RIFE as RIFE  # import from submodule
# External modules
from alive_progress import alive_bar
import cv2
import torch
from torch.nn import functional

DEFAULT_MULTIPLIER = 2

# Init device and model on import
if torch.cuda.is_available():
    print("Using PyTorch CUDA backend")
    pytorch_device = torch.device("cuda")
    torch.set_grad_enabled(False)
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True
else:
    print("Using PyTorch CPU backend")
    pytorch_device = torch.device("cpu")

rife_model = RIFE.Model()
rife_model.load_model(definitions.RIFE_MODEL)
rife_model.eval()
rife_model.device()

warnings.filterwarnings("ignore")  # Supress console warnings


def _read_image_dimensions(image_path):
    image = cv2.imread(image_path)
    image = (torch.tensor(image.transpose(2, 0, 1)).to(pytorch_device) / 255.).unsqueeze(0)
    n, c, height, width = image.shape
    return [height, width]


def _read_image(image_path):
    image = cv2.imread(image_path)
    image = (torch.tensor(image.transpose(2, 0, 1)).to(pytorch_device) / 255.).unsqueeze(0)
    n, c, height, width = image.shape
    padding_height = ((height - 1) // 32 + 1) * 32
    padding_width = ((width - 1) // 32 + 1) * 32
    padding = (0, padding_width - width, 0, padding_height - height)
    image = functional.pad(image, padding)
    return image


# def _write_image():
#     pass


def interpolate_file_mode(input0_file, input1_file, output_file):
    height, width = _read_image_dimensions(input0_file)
    image0 = _read_image(input0_file)
    image1 = _read_image(input1_file)

    output = rife_model.inference(image0, image1)  # Interpolation

    pathlib.Path(os.path.dirname(output_file)).mkdir(parents=True, exist_ok=True)  # Create output_folder

    cv2.imwrite(output_file,
                (output[0] * 255).byte().cpu().numpy().transpose(1, 2, 0)[:height, :width])  # Write to output


def interpolate_folder_mode(input_folder, output_folder):
    # List images in folder
    input_files_path = []
    for filePath in pathlib.Path(input_folder).glob('**/*'):  # List all files in the directory as their absolute path
        file_path_absolute = os.path.normpath(filePath.absolute())
        if file_path_absolute.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
            # Only adds files that have image extensions, fixes problems caused by "Thumbs.db"
            input_files_path.append(file_path_absolute)
    input_files_path.sort()

    # Read frame dimensions from first frame
    height, width = _read_image_dimensions(input_files_path[0])

    # Read files
    input_files = []
    for i in range(len(input_files_path)):
        # print(i)
        input_files.append(_read_image(input_files_path[i]))

    # Interpolate
    with alive_bar(len(input_files) * 2, enrich_print=False) as bar:
        output_files = []
        for j in range(len(input_files) - 1):
            # print(input_files_path[j], input_files_path[j + 1])
            mid = rife_model.inference(input_files[j], input_files[j + 1])
            output_files.append(input_files[j])
            bar()
            output_files.append(mid)
            bar()
        for _ in range(2):  # Duplicate last frame twice
            output_files.append(input_files[-1])
            bar()

    if os.path.isdir(output_folder):  # Delete output_folder if it exists to avoid conflicts
        shutil.rmtree(output_folder)
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)  # Create output_folder
    for i in range(len(output_files)):
        cv2.imwrite(os.path.join(output_folder, "{:06d}.png".format(i + 1)),
                    (output_files[i][0] * 255).byte().cpu().numpy().transpose(1, 2, 0)[:height, :width])
