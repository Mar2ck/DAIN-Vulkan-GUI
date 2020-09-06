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
parser.add_argument("-s", "--framemultiplier", help="Frame multiplier 2x,3x,etc (default=2)", action="store")
parser.add_argument("--verbose", help="Print additional info to the commandline", action="store_true")
#Dain-ncnn-vulkan passthrough options
parser.add_argument("-g", "--gpuid", help="GPU to use (default=auto) can be 0,1,2 for multi-gpu", action="store")
parser.add_argument("-t", "--tilesize", help="Tile size (>=128, default=256) must be multiple of 32 ,can be 256,256,128 for multi-gpu", action="store")
parser.add_argument("-j", "--threadcount", help="Thread count for load/process/save (default=1:2:2) can be 1:2,2,2:2 for multi-gpu", action="store")
args = parser.parse_args()

if args.framemultiplier == None:
	args.framemultiplier = "2"
try:
	MultiplierFloat = float(args.framemultiplier)
except:
	print("Multiplier not a valid number")

if args.gpuid == None:
	args.gpuid = "auto"
if args.tilesize == None:
	args.tilesize = "256"
if args.threadcount == None:
	args.threadcount = "1:2:2"

#Variables
DainVulkanLinuxLocation = os.path.abspath("./dain-ncnn-vulkan/dain-ncnn-vulkan-ubuntu-20.04/")
#DainVulkanWindowsLocation = os.path.abspath(".\\dain-ncnn-vulkan\\dain-ncnn-vulkan-windows-2019")
DainInputFolder = os.path.join(args.DainAppFolder, "original_frames")
DainInputFiles = sorted([f for f in listdir(DainInputFolder) if isfile(join(DainInputFolder, f))])
DainOutputFolder = os.path.join(args.DainAppFolder, "interpolated_frames")
if not os.path.exists(DainOutputFolder):
    os.makedirs(DainOutputFolder)
DainOutputFrameCount = str(len(DainInputFiles) * MultiplierFloat)

if args.verbose == True:
	print("Interpolation Multiplier:", args.framemultiplier)
	print("GPU Selection:", args.gpuid)
	print("Tilesize:", args.tilesize)
	print("Threads:", args.threadcount)
	print("Outputframe Count:", DainOutputFrameCount)
	print("Platform:", sys.platform)

#DAIN Process Functions
def DainVulkanFileModeCommand(Input0File, Input1File, OutputFile, TimeStep):
	#Default to 0.5 if not specified
	if TimeStep == None:
		TimeStep = "0.5"
	subprocess.run(["./dain-ncnn-vulkan", "-0", os.path.abspath(Input0File), "-1", os.path.abspath(Input1File), "-o", os.path.abspath(OutputFile), "-s", TimeStep, "-t", args.tilesize, "-g", args.gpuid, "-j", args.threadcount], cwd=DainVulkanLinuxLocation)

def DainVulkanFolderModeCommand(InputFolder, OutputFolder, TargetFrames):
	if sys.platform == "win32":
		subprocess.run([".\\dain-ncnn-vulkan.exe", "-i", os.path.abspath(InputFolder), "-o", os.path.abspath(OutputFolder), "-n", TargetFrames, "-t", args.tilesize, "-g", args.gpuid, "-j", args.threadcount])
	else:
		subprocess.run(["./dain-ncnn-vulkan", "-i", os.path.abspath(InputFolder), "-o", os.path.abspath(OutputFolder), "-n", TargetFrames, "-t", args.tilesize, "-g", args.gpuid, "-j", args.threadcount], cwd=DainVulkanLinuxLocation)


DainVulkanFolderModeCommand(DainInputFolder, DainOutputFolder, DainOutputFrameCount)

#Mode 1&2 Implement
#currentFileName = 1
# for FileNumber in range(len(DainInputFiles)):
# 	#Copy Original Frames
# 	currentFrame = os.path.join(DainInputFolder, DainInputFiles[FileNumber])
# 	nextFrame = os.path.join(DainInputFolder, DainInputFiles[FileNumber + 1])
# 	copyFrameTo = os.path.join(DainOutputFolder, ("{:010d}".format(currentFileName) + ".png"))
# 	#print(currentFrame)
# 	print(copyFrameTo)
# 	#print(nextFrame)
# 	copyfile(currentFrame, copyFrameTo)
#
# 	#Interpolate New Frames
# 	interpolatedFrame = os.path.join(DainOutputFolder, ("{:010d}".format(currentFileName + 1) + ".png"))
# 	#print(interpolatedFrame)
# 	DainVulkanFileModeCommand(currentFrame, nextFrame, interpolatedFrame, None)
#
# 	currentFileName = currentFileName + args.framemultiplier

