# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 20:45:46 2019

@author: wayne
"""


from is_rast import is_rast
from metadata import metadata

import os
import arcpy
import numpy




def decibel_convert(filename):
    """
    Converts the input UAVSAR .grd file into units of decibels. Note
    that a .hdr file must be created and accompany the .grd/.inc files for this to work

    :param filename:    the full file path string for the .grd data file
    :return outname:    filepath to output file created by this function.
    """

    #arcpy.CheckOutExtension("Spatial")

    inRaster, meta = raster.to_numpy(filename)
    dB_raster = 10 * numpy.log10(inRaster)
    outname = filename.replace(".grd", "_dB.tif")
    raster.from_numpy(dB_raster, meta, outname)
    return outname
