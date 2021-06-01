# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 16:52:52 2020

@author: wayne
"""

import sys
import os
import numpy as np 
from osgeo import gdal, gdalconst 
from osgeo.gdalconst import * 
import rasterio
from create_header import create_bin_header
from create_header import create_bmp_header
from ConvertHDR2Geotiff import load_ENVI_data
from ConvertHDR2Geotiff import load_BMP_data
from ConvertHDR2Geotiff import array2raster




######################################################################
###############Users input parameters ###############
#####################################################################

workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar_experiment'

#input
#InputDatafolder='UA_neuser_32023_18065_002_180918_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18065_Cols'
#OutputDataFolder='UA_neuser_32023_18065_Processing'

#InputDatafolder='UA_neuser_32023_18066_000_180919_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18066_Cols'
#OutputDataFolder='UA_neuser_32023_18066_Processing'

#InputDatafolder='UA_neuser_32023_18067_000_180920_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18067_Cols'
#OutputDataFolder='UA_neuser_32023_18067_Processing'

InputDatafolder='UA_neuser_32023_18068_000_180922_L090_CX_01'
GeoTiffOutputFolder='UA_neuser_32023_18068_Cols'
OutputDataFolder='UA_neuser_32023_18068_Processing'

#InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18069_Cols'
#OutputDataFolder='UA_neuser_32023_18069_Processing'


Parameter_Pauli_od=workstation+"/"+OutputDataFolder+"/Pauli"
Parameter_id=workstation+"/"+InputDatafolder 

######################################################################
########Create hdr for the Pauli files###########
#####################################################################
#subfolder='\\UA_neuser_32023_18067_000_180920_L090_CX_01\\'




T3Folder=Parameter_Pauli_od+'/'#workstation+subfolder+'Pauli\\'
annfolder=Parameter_id+'/'#workstation+subfolder

#create bmp hdr file
create_bmp_header(T3Folder,annfolder)
#not needed since the inc and hgt can use the same hdr file
#create_hgt_header(workstation+subfolder)


######################################################################
########Convert to geotiff (hgt, inc, and mask files) ###########
#####################################################################


def readSourceMeta(InputFile):
    #get the raster object
    RasterObj = rasterio.open(InputFile)
    
    #get the meta info from source file
    Source_meta=RasterObj.meta.copy()
    
    return Source_meta






## Open mask file and convert it to tiff
#mask_file_name=workstation+subfolder+\
#"T3\\mask_valid_pixels.bin"

BMP_file_name=T3Folder+\
"PauliRGB.bmp"
BMP_image_array = load_BMP_data(BMP_file_name)

# Write it out as a geotiff
Pauli_Geotiff_out=T3Folder+\
"\\PauliRGBGeotiff.tif"

#read meta from hgt data
Source_meta=readSourceMeta(Parameter_id+'\\neuser_32023_18068_000_180922_L090_CX_01_hgt.tif')

print(Source_meta)

#update the meta
Source_meta.update(
    driver='GTiff',
    dtype=rasterio.float32,
    count='3',   
    compress='lzw')

# get the export file name token
dataVar=os.path.splitext(os.path.basename(BMP_file_name))[0]
    
#and then save the variable as geotiff format
file_out=path+'\\'+dataVar+"_PCA1_noStand"+".tif"

# Write it out as a geotiff    
with rasterio.open(file_out, "w", **Source_meta) as dest:
    dest.write(BMP_image_array.astype(rasterio.float32),1)




       
#   
#### Open hgt and convert it to tif
#hgt_file_name=Parameter_if_hgt
##read the data
#data, geodata = load_ENVI_data(hgt_file_name)
#
## Write it out as a geotiff
#hgt_filenameNoExt=os.path.splitext(os.path.basename(hgt_file_name))[0]
#hgt_file_out=workstation+'\\'+GeoTiffOutputFolder+'\\UA_'+hgt_filenameNoExt+\
#"_hgt.tif"
##convert hgt from bin format to tif format
#array2raster(data, geodata, hgt_file_out, gdal_driver='GTiff') 
#
#### Open inc and convert it to tif
##inc_file_name=Parameter_id+'\\'+\
##"neuser_32023_18067_000_180920_L090_CX_01.inc"
#
#inc_file_name=Parameter_id+'\\'+IncFiles
#data, geodata = load_ENVI_data(inc_file_name)
#
## Write it out as a geotiff
#inc_file_out=workstation+'\\'+GeoTiffOutputFolder+'\\UA_'+\
#os.path.splitext(os.path.basename(IncFiles))[0]+"_inc.tif"
#array2raster(data, geodata, inc_file_out, gdal_driver='GTiff')
