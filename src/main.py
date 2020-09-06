#!/usr/bin/env python3
try:
	import subprocess
	import sys
	import os
	import argparse
	import platform
	from shutil import copyfile
	from os import listdir
	from os.path import isfile, join
except ImportError as err:
	print("Error: ", err)
	print("Could not import modules. Make sure all dependencies are installed.")
	exit(1)

#Console arguments
parser = argparse.ArgumentParser()
parser.add_argument("DainAppFolder")
parser.add_argument("-g", "--gpuid", help="GPU to use (Default=0)", action="store")
args = parser.parse_args()

if args.gpuid == None:
	DainGpuID = "0"
else:
	DainGpuID = args.gpuid

#Variables
DainVulkanLocation = os.path.abspath("./dain-ncnn-vulkan/dain-ncnn-vulkan-ubuntu-20.04/")
DainInputFolder = os.path.join(args.DainAppFolder, "original_frames")
DainInputFiles = sorted([f for f in listdir(DainInputFolder) if isfile(join(DainInputFolder, f))])
DainOutputFolder = os.path.join(args.DainAppFolder, "interpolated_frames")
InterpolateMultiplier = 2

#DAIN Process Function
def DainVulkanCommand(Input0File, Input1File, OutputFile, TimeStep):
	#Default to 0.5 if not specified
	if TimeStep == None:
		TimeStep = "0.5"
	subprocess.run(["./dain-ncnn-vulkan", "-0", os.path.abspath(Input0File), "-1", os.path.abspath(Input1File), "-o", os.path.abspath(OutputFile), "-s", TimeStep, "-g", DainGpuID], cwd=DainVulkanLocation)

#DainVulkanCommand("0.png", "10.png", "5.png", None)

#Mode 1&2 Implement
currentFileName = 1
for FileNumber in range(len(DainInputFiles)):
	#Copy Original Frames
	currentFrame = os.path.join(DainInputFolder, DainInputFiles[FileNumber])
	nextFrame = os.path.join(DainInputFolder, DainInputFiles[FileNumber + 1])
	copyFrameTo = os.path.join(DainOutputFolder, ("{:010d}".format(currentFileName) + ".png"))
	#print(currentFrame)
	print(copyFrameTo)
	#print(nextFrame)
	copyfile(currentFrame, copyFrameTo)
		
	#Interpolate New Frames
	interpolatedFrame = os.path.join(DainOutputFolder, ("{:010d}".format(currentFileName + 1) + ".png"))
	#print(interpolatedFrame)
	DainVulkanCommand(currentFrame, nextFrame, interpolatedFrame, None)
	
	currentFileName = currentFileName + InterpolateMultiplier

