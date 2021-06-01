# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 14:54:49 2019
revised from calcSlopeDegrees

@author: wayne
"""
#! /usr/bin/env python
####################################################################################
# calcSlopeDegrees.py
#
# A Python script to calculate slope from a DEM, where the horizontal spacing is in degrees
# latitude and longitude.
#
# Requires RIOS (https://bitbucket.org/chchrsc/rios/) to read image
#
# The base slope calculation is in Python. If Numba (http://numba.pydata.org)
# is available this is used to improve speed.
# For the best speed a Fortran function (slope.f) is available to perform the slope calculation.
# This must be compiled using:
#
# f2py -llapack -c slope.f90 -m slope
# 
# Dan Clewley (daniel.clewley@gmail.com) - 26/06/2013
#
# Adapted from EASI code by Jane Whitcomb
#
#
# Copyright 2014 Daniel Clewley & Jane Whitcomb.
# 
# Permission is hereby granted, free of charge, to any person 
# obtaining a copy of this software and associated documentation 
# files (the "Software"), to deal in the Software without restriction, 
# including without limitation the rights to use, copy, modify, 
# merge, publish, distribute, sublicense, and/or sell copies of the 
# Software, and to permit persons to whom the Software is furnished 
# to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be 
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES 
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR 
# ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

####################################################################################

from rios import imagereader
import sys,os
sys.path.append(os.sys.path[0])
from rios.imagewriter import ImageWriter
import numpy as np
from math import sqrt

#from calcSlopeDegrees_co import slopePython
##slopePython(inBlock, outBlock, inXSize, inYSize, zScale=1)
#from calcSlopeDegrees_co import calcSlope
##calcSlope(inBlock, inXSize, inYSize, fitPlane=False, zScale=1, winSize=3, minSlope=None)

def getPixelSize(lat, latsize, lonsize):
    """ Get the pixel size (in m) based on latitude and
        pixel size in degrees
    """

    # Set up parameters for elipse
    # Semi-major and semi-minor for WGS-84 ellipse
    ellipse = [6378137.0, 6356752.314245]
    
    radlat = np.deg2rad(lat)
    
    Rsq = (ellipse[0]*np.cos(radlat))**2+(ellipse[1]*np.sin(radlat))**2
    Mlat = (ellipse[0]*ellipse[1])**2/(Rsq**1.5)
    Nlon = ellipse[0]**2/np.sqrt(Rsq)
    xsize = np.pi/180*np.cos(radlat)*Nlon*lonsize
    ysize = np.pi/180*Mlat*latsize

    return xsize, ysize


def slopePython(inBlock, outBlock, inXSize, inYSize, zScale=1):

    """ Calculate slope using Python.
        If Numba is available will make use of autojit function
        to run at ~ 1/2 the speed of the Fortran module. 
        If not will fall back to pure Python - which will be slow!
    """
    for x in range(1,inBlock.shape[2]-1):
        for y in range(1, inBlock.shape[1]-1):
            # Get window size
            dx = 2 * inXSize[y,x]
            dy = 2 * inYSize[y,x]

            # Calculate difference in elevation
            dzx = (inBlock[0,y,x-1] - inBlock[0,y,x+1])*zScale
            dzy = (inBlock[0,y-1,x] - inBlock[0,y+1,x])*zScale

            # Find normal vector to the plane
            nx = -1 * dy * dzx
            ny = -1 * dx * dzy
            nz = dx * dy
    
            slopeRad = np.arccos(nz / sqrt(nx**2 + ny**2 + nz**2))
            slopeDeg = (180. / np.pi) * slopeRad
    
            outBlock[0,y,x] = slopeDeg
   
    return outBlock

def calcSlope(inBlock, inXSize, inYSize, zScale=1, minSlope=None):
    """ Calculates slope for a block of data
        Arrays are provided giving the size for each pixel.

        * inBlock - In elevation
        * inXSize - Array of pixel sizes (x)
        * inYSize - Array of pixel sizes (y)
        * fitPlane - Calculate slope by fitting a plane to elevation 
                     data using least squares fitting.
        * zScale - Scaling factor between horizontal and vertical
    """
    # Otherwise run through loop in python (which will be slower)
    # Setup output block
    outBlock = np.zeros_like(inBlock, dtype=np.float32)
    slopePython(inBlock, outBlock, inXSize, inYSize, zScale)

    if minSlope is not None:
        # Set very low values to constant
        outBlock[0] = np.where(np.logical_and(outBlock[0] > 0,outBlock[0] < minSlope),minSlope,outBlock[0])

    return(outBlock)
#
##with open('out.bin', 'wb') as f:
##INPUT AND OUTPUT 
#directory='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\'+\
#'uavsar.asfdaac.alaska.edu\\'
#maskfile=directory +\
#"Processing\\T3\\"+ "mask_valid_pixels.tif"
#demfile=directory +\
#"UA_neuser_32023_18067_000_180920_L090_CX_01\\"+ \
#"neuser_32023_18067_000_180920_L090_CX_01_hgt.tif"
#
#slopeFile=directory+'test_slope.tif'
#
#outImage=slopeFile
#
#winSize=3
#
## Set up RIOS image reader
#reader = imagereader.ImageReader(demfile,windowxsize=1024, windowysize=1024, overlap=int(winSize/2))
#
#writer = None
#
#print("Starting...")
#
#zScale=1
##args.spacing_degrees
#hDegree = True
#
#minSlope=None
#
##This class is the opposite of the ImageReader class 
##and is designed to be used in conjunction. 
##The easiest way to use it is pass the info returned by 
##the ImageReader for first iteration to the constructor. 
##Otherwise, image size etc must be passed in.
#for (info, inBlock) in reader:
#
#    # Get percent complete
#    sys.stdout.write("\r %i Percent Complete"%(int(info.getPercent())))
#
#    # Get coordinates for block
#    xCoords, yCoords = info.getBlockCoordArrays()
#
#    # Convert pixel sizes to m (if in degrees).
#    xres, yres = info.getPixelSize()
#    if hDegree:
#        xSize, ySize = getPixelSize(yCoords, xres, yres)
#    else:
#        xSize = np.zeros_like(xCoords)
#        ySize = np.zeros_like(yCoords)
#        xSize[...] = xres
#        ySize[...] = yres
#
#    outBlock = calcSlope(inBlock, xSize, ySize,  zScale, winSize, minSlope)
#
#    # Check if writer exists, create one if not.
#    if writer is None:
#        writer = ImageWriter(outImage, info=info, firstblock=outBlock) 
#    else:
#        writer.write(outBlock)
#
#sys.stdout.write("\r 100 Percent Complete\n")
#calcStats = True
#if calcStats:
#    # Close and calculate stats (for faster display)
#    print("Writing stats...")
#    writer.close(calcStats=True)
#else:
#    writer.close(calcStats=False)
#print("Done")