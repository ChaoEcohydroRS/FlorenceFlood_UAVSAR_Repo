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

import sys,os
sys.path.append(os.sys.path[0])
from rios import imagereader
from rios.imagewriter import ImageWriter
import argparse
import numpy as np
from math import sqrt

useFortranSlope=True
haveNumba = False

try:
    import slope
except ImportError:
    useFortranSlope=False

try:
    from numba import autojit
    if useFortranSlope:
        print('Numba is available - using Fortran module instead')
    else:
        print('Fortran module not available - using Numba instead')
    haveNumba = True
except ImportError:
    if not useFortranSlope:
        print('Warning: Could not import Numba or Fortran slope module - will be about 50 x slower!')
    else:
        print('Fortran module is available')
    # have to define our own autojit so Python doesn't complain
    def autojit(func):
        return func

@autojit
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

def slopePythonPlane(inBlock, outBlock, inXSize, inYSize, A_mat, z_vec, winSize=3, zScale=1):

    """ Calculate slope using Python.

        Algorithm fits plane to a window of data and calculated the slope
        from this - slope than the standard algorithm but can deal with
        noisy data batter.

        The matrix A_mat (winSize**2,3) and vector zScale (winSize**2) are allocated
        outside the function and passed in.
    """

    winOffset = int(winSize/2)

    for x in range(winOffset-1,inBlock.shape[2]):
        for y in range(winOffset-1, inBlock.shape[1]):
            # Get window size
            dx = winSize * inXSize[y,x]
            dy = winSize * inYSize[y,x]

            # Calculate difference in elevation
            """ 
                Solve A b = x to give x
                Where A is a matrix of:
                    x_pos | y_pos | 1
                and b is elevation
                and x are the coefficents
            """
 
            # Form matrix
            index = 0
            for i in range(-1*winOffset, winOffset+1):
                for j in range(-1*winOffset, winOffset+1):

                    A_mat[index,0] = 0+(i*inXSize[y,x])
                    A_mat[index,1] = 0+(j*inYSize[y,x])
                    A_mat[index,2] = 1

                    # Elevation
                    z_vec[index] = inBlock[0,y+j,x+i]*zScale

                    index+=1
            
            # Linear fit
            coeff_vec = np.linalg.lstsq(A_mat, z_vec)[0]
 
            # Calculate dzx and dzy
            dzx = coeff_vec[0] * dx
            dzy = coeff_vec[1] * dy
    
            # Find normal vector to the plane
            nx = -1 * dy * dzx
            ny = -1 * dx * dzy
            nz = dx * dy
    
            slopeRad = np.arccos(nz / sqrt(nx**2 + ny**2 + nz**2))
            slopeDeg = (180. / np.pi) * slopeRad
    
            outBlock[0,y,x] = slopeDeg
   
    return outBlock


def calcSlope(inBlock, inXSize, inYSize, fitPlane=False, zScale=1, winSize=3, minSlope=None):
    """ Calculates slope for a block of data
        Arrays are provided giving the size for each pixel.

        * inBlock - In elevation
        * inXSize - Array of pixel sizes (x)
        * inYSize - Array of pixel sizes (y)
        * fitPlane - Calculate slope by fitting a plane to elevation 
                     data using least squares fitting.
        * zScale - Scaling factor between horizontal and vertical
        * winSize - Window size to fit plane over.
    """
    # Otherwise run through loop in python (which will be slower)
    # Setup output block
    outBlock = np.zeros_like(inBlock, dtype=np.float32)
    slopePython(inBlock, outBlock, inXSize, inYSize, zScale)

    if minSlope is not None:
        # Set very low values to constant
        outBlock[0] = np.where(np.logical_and(outBlock[0] > 0,outBlock[0] < minSlope),minSlope,outBlock[0])

    return(outBlock)

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
    
# Set up options
parser = argparse.ArgumentParser()
parser.add_argument("inimage", nargs=1,type=str, help="Input DEM")
parser.add_argument("outimage", nargs=1,type=str, help="Output Slope image")
parser.add_argument("--nostats", action='store_true', default=False, help="Don't calculate stats for output slope image.")
parser.add_argument("--plane_ls", action='store_true', default=False, help="Calculate slope by fitting a plane to a window of elevation data using least squares fitting.")
parser.add_argument("--min_slope", type=float, default=None, help="Set minimum value for slope (values smaller than this but greater than 0 will be fixed to this value)")
parser.add_argument("--window_size", type=int, default=3, help="Window size to calculate slope over when using least squares fitting (default 3)")
parser.add_argument("--z_scale", type=int, default=1, help="Scaling factor between horizontal (m) and vertical. Assumed 1 (vertical units are metres).")
parser.add_argument("--spacing_degrees", action='store_true', default=False, help="Pixel size is in degrees - converted to metres based on latitude.")

args = parser.parse_args() 

inImage = args.inimage[0]
outImage = args.outimage[0]

zScale = args.z_scale
winSize = args.window_size

fitPlane = args.plane_ls

if not fitPlane and winSize != 3:
    print("ERROR: Setting window size is only supported with '--plane_ls'")
    sys.exit()

if fitPlane and not useFortranSlope:
    print("WARNING: Couldn't import Fortran module, Numba isn't supported for plane fitting")

calcStats = True
if args.nostats:
    calcStats = False

minSlope = args.min_slope

hDegree = args.spacing_degrees

# Set up RIOS image reader
reader = imagereader.ImageReader(inImage, overlap=int(winSize/2))

writer = None

print("Starting...")

for (info, inBlock) in reader:

    # Get percent complete
    sys.stdout.write("\r %i Percent Complete"%(int(info.getPercent())))

    # Get coordinates for block
    xCoords, yCoords = info.getBlockCoordArrays()

    # Convert pixel sizes to m (if in degrees).
    xres, yres = info.getPixelSize()
    if hDegree:
        xSize, ySize = getPixelSize(yCoords, xres, yres)
    else:
        xSize = np.zeros_like(xCoords)
        ySize = np.zeros_like(yCoords)
        xSize[...] = xres
        ySize[...] = yres

    outBlock = calcSlope(inBlock, xSize, ySize, fitPlane, zScale, winSize, minSlope)

    # Check if writer exists, create one if not.
    if writer is None:
        writer = ImageWriter(outImage, info=info, firstblock=outBlock) 
    else:
        writer.write(outBlock)

sys.stdout.write("\r 100 Percent Complete\n")

if calcStats:
    # Close and calculate stats (for faster display)
    print("Writing stats...")
    writer.close(calcStats=True)
else:
    writer.close(calcStats=False)
print("Done")


