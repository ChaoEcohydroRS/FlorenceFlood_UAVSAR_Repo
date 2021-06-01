# -*- coding: utf-8 -*-
"""
Spyder Editor
@author: wayne
This is a temporary script file.
"""
import sys
import os
import numpy as np 
from osgeo import gdal, gdalconst 
from osgeo.gdalconst import * 
import glob

def load_ENVI_data(file_name, gdal_driver='ENVI'):
    '''
    Converts a GDAL compatable file into a numpy array and associated geodata.
    The rray is provided so you can run with your processing - the geodata consists of the geotransform and gdal dataset object
    If you're using an ENVI binary as input, this willr equire an associated .hdr file otherwise this will fail.
    This needs modifying if you're dealing with multiple bands.
    
    VARIABLES
    file_name : file name and path of your file
    
    RETURNS
    image array
    (geotransform, inDs)
    '''
    driver = gdal.GetDriverByName(gdal_driver) ## http://www.gdal.org/formats_list.html
    driver.Register()

    inDs = gdal.Open(file_name, GA_ReadOnly)

    if inDs is None:
        print("Couldn't open this file: %s" %(file_name))
        print('/nPerhaps you need an ENVI .hdr file? A quick way to do this is to just open the binary up in ENVI and one will be created for you.')
        sys.exit("Try again!")
    else:
        print("%s opened successfully" %file_name)
        
    # Extract some info form the inDs         
    geotransform = inDs.GetGeoTransform()

    # Get the data as a numpy array
    band = inDs.GetRasterBand(1)
    cols = inDs.RasterXSize
    rows = inDs.RasterYSize
    image_array = band.ReadAsArray(0, 0, cols, rows)
    
    return image_array, (geotransform, inDs)


def load_GTiff_data(file_name, gdal_driver='GTiff'):
    '''
    Converts a GDAL compatable file into a numpy array and associated geodata.
    The rray is provided so you can run with your processing - the geodata consists of the geotransform and gdal dataset object
    If you're using an ENVI binary as input, this willr equire an associated .hdr file otherwise this will fail.
    This needs modifying if you're dealing with multiple bands.
    
    VARIABLES
    file_name : file name and path of your file
    
    RETURNS
    image array
    (geotransform, inDs)
    '''
    driver = gdal.GetDriverByName(gdal_driver) ## http://www.gdal.org/formats_list.html
    driver.Register()

    inDs = gdal.Open(file_name, GA_ReadOnly)

    if inDs is None:
        print("Couldn't open this file: %s" %(file_name))
        print('/nPerhaps you need an ENVI .hdr file? A quick way to do this is to just open the binary up in ENVI and one will be created for you.')
        sys.exit("Try again!")
    else:
        print("%s opened successfully" %file_name)
        
    # Extract some info form the inDs         
    geotransform = inDs.GetGeoTransform()

    # Get the data as a numpy array
    band = inDs.GetRasterBand(1)
    cols = inDs.RasterXSize
    rows = inDs.RasterYSize
    image_array = band.ReadAsArray(0, 0, cols, rows)
    
    return image_array, (geotransform, inDs)

def load_BMP_data(file_name, gdal_driver='BMP'):
    '''
    Converts a GDAL compatable file into a numpy array and associated geodata.
    The rray is provided so you can run with your processing - the geodata consists of the geotransform and gdal dataset object
    If you're using an ENVI binary as input, this willr equire an associated .hdr file otherwise this will fail.
    This needs modifying if you're dealing with multiple bands.
    
    VARIABLES
    file_name : file name and path of your file
    
    RETURNS
    image array
    (geotransform, inDs)
    '''
    driver = gdal.GetDriverByName(gdal_driver) ## http://www.gdal.org/formats_list.html
    driver.Register()

    inDs = gdal.Open(file_name, GA_ReadOnly)

    if inDs is None:
        print("Couldn't open this file: %s" %(file_name))
        print('/nPerhaps you need an .hdr file? A quick way to do this is to just open the binary up in BMP and one will be created for you.')
        sys.exit("Try again!")
    else:
        print("%s opened successfully" %file_name)
        
    # Extract some info form the inDs         
    #geotransform = inDs.GetGeoTransform()

    # Get the data as a numpy array
    band = inDs.GetRasterBand(1)
    cols = inDs.RasterXSize
    rows = inDs.RasterYSize
    image_array = band.ReadAsArray(0, 0, cols, rows)
    
    return image_array#, (geotransform, inDs)



def array2raster(data_array, geodata, file_out, gdal_driver='GTiff'):
    '''
    Converts a numpy array to a specific geospatial output
    If you provide the geodata of the original input dataset, then the output array will match this exactly.
    If you've changed any extents/cell sizes, then you need to amend the geodata variable contents (see below)
    
    VARIABLES
    data_array = the numpy array of your data
    geodata = (geotransform, inDs) # this is a combined variable of components when you opened the dataset
                inDs = gdal.Open(file_name, GA_ReadOnly)
                geotransform = inDs.GetGeoTransform()
                see data2array()
    file_out = name of file to output to (directory must exist)
    gdal_driver = the gdal driver to use to write out the data (default is geotif) - see: http://www.gdal.org/formats_list.html

    RETURNS
    None
    '''

    if not os.path.exists(os.path.dirname(file_out)):
        print("Your output directory doesn't exist - please create it")
        print("No further processing will take place.")
    else:
        post1=geodata[0][1]
        post2=geodata[0][5]
        print(post1)
        print(post2)       
        
        original_geotransform, inDs = geodata
        print(original_geotransform)
#        print(original_geotransform[0])

        rows, cols = data_array.shape
        bands = 1

        # Set the gedal driver to use
        driver = gdal.GetDriverByName(gdal_driver) 
        driver.Register()

        # Creates a new raster data source
        #dstImg = driver.Create(dstName, srcImg.RasterXSize, 
        #srcImg.RasterYSize, 1, gdal.GDT_Int32, options = [ 'COMPRESS=DEFLATE' ])
        outDs = driver.Create(file_out, cols, rows, bands, gdal.GDT_Float32, ['COMPRESS=LZW'])

        # Write metadata
        originX = original_geotransform[0]
        
        originY = original_geotransform[3]
        

        outDs.SetGeoTransform([originX, post1, 0.0, originY, 0.0, post2])
        outDs.SetProjection(inDs.GetProjection())

        #Write raster datasets
        outBand = outDs.GetRasterBand(1)
        outBand.WriteArray(data_array)
            
        print("Output saved: %s" %file_out)


workstation='D:\\Data\\UAVSAR'
workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar_experiment'

##input
#InputDatafolder='UA_neuser_32023_18065_002_180918_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18065_Cols'
#OutputDataFolder='UA_neuser_32023_18065_Processing'

#InputDatafolder='UA_neuser_32023_18067_000_180920_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18067_Cols'
#OutputDataFolder='UA_neuser_32023_18067_Processing'

InputDatafolder='UA_neuser_32023_18068_000_180922_L090_CX_01'
GeoTiffOutputFolder='UA_neuser_32023_18068_Cols'
OutputDataFolder='UA_neuser_32023_18068_Processing'
#
#
#InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18069_Cols'
#OutputDataFolder='UA_neuser_32023_18069_Processing'


       
# Open some data inc /neuser_32023_18067_000_180920_L090_CX_01.hgt
In_file_folder=workstation + "\\" + OutputDataFolder +"\\SMS\\"
print(In_file_folder)

os.chdir(In_file_folder)
for In_file_name in glob.glob("Dbl*.tif"):
    print(In_file_name)
    data, geodata = load_GTiff_data(In_file_name)
    
    #Write it out as a geotiff
    file_out=workstation + "\\" + OutputDataFolder +"\\SMS\\" + InputDatafolder + "_R_FV.tif"
    array2raster(data, geodata, file_out, gdal_driver='GTiff') 

        
### Open some data C:\Workstation\NC_Study\UAVSAR\Data\uavsar.asfdaac.alaska.edu\Processing\T3 
#file_name="C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar.asfdaac.alaska.edu\\"+\
#"Processing\\T3\\mask_valid_pixels.bin"
#data, geodata = load_data(file_name)
#
## Write it out as a geotiff
#file_out="C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar.asfdaac.alaska.edu\\"+\
#"Processing\\T3\\mask_valid_pixels.tif"
#array2raster(data, geodata, file_out, gdal_driver='GTiff')           

#T11
#T12_imag
#'T11','T12_imag',
#
##the list to be applied
#PolarimetricList=['T22','T33','T12_real',\
#                 'T13_imag','T13_real','T23_imag','T23_real']
#
#for T3CMRasterName in PolarimetricList:
#    dataVar=T3CMRasterName
#    
#    ## Open some data inc /neuser_32023_18067_000_180920_L090_CX_01.hgt
#    file_name="C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar_experiment\\"+\
#    "Processing\\T3\\"+dataVar+".bin"
#    data, geodata = load_data(file_name)
#    
#    # Write it out as a geotiff
#    file_out="C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar_experiment\\"+\
#    "UA_neuser_32023_18067_000_180920_L090_CX_01_"+dataVar+".tif"
#    array2raster(data, geodata, file_out, gdal_driver='GTiff') 
#
#       