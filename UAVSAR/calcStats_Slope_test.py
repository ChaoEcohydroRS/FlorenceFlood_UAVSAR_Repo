# -*- coding: utf-8 -*-
"""
Created on Sat Dec 28 21:47:52 2019

@author: wayne
"""
#from metadata import metadata
import math
import os
#import arcpy
import richdem as rd
import numpy as np
import rasterio
from osgeo import gdal
from rasterio.features import dataset_features
from rasterio.vrt import WarpedVRT
from shapely.geometry import shape, mapping
from calcSlopeDegrees_Revised import calcSlope
from calcSlopeDegrees_Revised import slopePython
from calcSlopeDegrees_Revised import getPixelSize

from rios import imagereader
import sys


demfile='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar_experiment\\'+\
'UA_neuser_32023_18067_Cols\\UA_neuser_32023_18067_000_180920_L090_CX_01_hgt.tif'

windowxsize=200
#the size of overlap window
OverlapSize=3

windowxsize=2048#20788#

windowysize=2048#19504#


zScale=1
#args.spacing_degrees
hDegree = True


# Set up RIOS image reader
reader = imagereader.ImageReader(demfile,\
         windowxsize=windowxsize, windowysize=windowysize, overlap=int(OverlapSize))

writer = None

print("Starting...")

#This class is the opposite of the ImageReader class 
#and is designed to be used in conjunction. 
#The easiest way to use it is pass the info returned by 
#the ImageReader for first iteration to the constructor. 
#Otherwise, image size etc must be passed in.
for (info, inBlock) in reader:

    # Get percent complete
    sys.stdout.write("\r %i Percent Complete"%(int(info.getPercent())))

    # Get coordinates for block
    xCoords, yCoords = info.getBlockCoordArrays()
    print(xCoords)

    # Convert pixel sizes to m (if in degrees).
    xres, yres = info.getPixelSize()
    if hDegree:
        xSize, ySize = getPixelSize(yCoords, xres, yres)
    else:
        xSize = np.zeros_like(xCoords)
        ySize = np.zeros_like(yCoords)
        xSize[...] = xres
        ySize[...] = yres

#    outBlock = calcSlope(inBlock, xSize, ySize, zScale, minSlope)
#
#    # Check if writer exists, create one if not.
#    if writer is None:
#        writer = ImageWriter(CalcSlopeFile, info=info, firstblock=outBlock) 
#    else:
#        writer.write(outBlock)

sys.stdout.write("\r 100 Percent Complete\n")

calcStats = True

if calcStats:
    # Close and calculate stats (for faster display)
    print("Writing stats...")
    writer.close(calcStats=True)
else:
    writer.close(calcStats=False)
print("Done")