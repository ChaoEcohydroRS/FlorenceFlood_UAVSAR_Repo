# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 10:32:16 2019
True azimuth across-range-look direction
@author: wayne
"""

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

directory='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\'+\
'uavsar.asfdaac.alaska.edu\\'

s3_path=directory +\
"Processing\\T3\\"+ "mask_valid_pixels.tif"

decim=1

with rasterio.open(s3_path) as src:
    with WarpedVRT(src, nodata=0) as vrt:
                feat = list(dataset_features(vrt, bidx=1, sampling=decim, band=False))[0]
                
#since the feat is so complex, we would like to simplify it 
boundsgeometry = shape(feat["geometry"])
feat["geometry"] = mapping(boundsgeometry.simplify(0.01))
coords=feat["geometry"]['coordinates']

coordsList=list(coords[0])
LonList = []
LonList.append([e[0] for e in coordsList])

LatList = []
LatList.append([e[1] for e in coordsList])


minLon=min(LonList[0])
maxLon = max(LonList[0])

minLat = min(LatList[0])
maxLat = max(LatList[0])
print(minLon,maxLon,minLat,maxLat)

trueAzimuth = \
math.atan2(LatList[0][LonList[0].index(minLon)]-minLat, \
            (LonList[0][LatList[0].index(minLat)]-minLon))*(180.0/math.pi)+270.0

#True azimuth across-range-look direction
RangeLookDir=trueAzimuth-90.0

print(RangeLookDir)