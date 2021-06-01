# -*- coding: utf-8 -*-
"""
Created on Sat May  9 18:01:02 2020

@author: wayne
"""
import glob
import os
from osgeo import gdal
from gdalconst import GA_ReadOnly
import shutil


def _func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder):
    #workstation
    Workpath=workstation + '\\' + GeoTiffOutputFolder + '\\' 
    
    #get all elements of the P matrix as a list to be applied
    #and just select one
    PolarizationGeotiff_List=[]
    os.chdir(Workpath)
    for file in glob.glob("*_D_*.tif"):
        PolarizationGeotiff_List.append(file)
        
    # input one polarization image as mask raster
    inputMaskRaster=Workpath + PolarizationGeotiff_List[0]
    
    maskDs = gdal.Open(inputMaskRaster, GA_ReadOnly)
    projection=maskDs.GetProjectionRef()
    geoTransform = maskDs.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * maskDs.RasterXSize
    miny = maxy + geoTransform[5] * maskDs.RasterYSize
    
    #get the IA raster
    IARasterGeotiff_List=[]
    os.chdir(Workpath)
    for file in glob.glob("*_IA.tif"):
        IARasterGeotiff_List.append(file)
    
    #the data needs to mask
    inputRaster=Workpath + IARasterGeotiff_List[0]
    
    IA_Ds = gdal.Open(inputRaster, GA_ReadOnly)
    IA_geoTransform = IA_Ds.GetGeoTransform()
    IA_minx = IA_geoTransform[0]
    IA_maxy = IA_geoTransform[3]
    IA_maxx = IA_minx + IA_geoTransform[1] * IA_Ds.RasterXSize
    IA_miny = IA_maxy + IA_geoTransform[5] * IA_Ds.RasterYSize
    
    
    
    if [minx,maxy,maxx,miny] != [IA_minx,IA_maxy,IA_maxx,IA_miny] :    
        translateOptions = gdal.TranslateOptions(format = 'GTiff',
                                                 projWin=[minx,maxy,maxx,miny],
                                                 outputSRS=projection,
                                                 creationOptions = ['TFW=YES', 'COMPRESS=LZW'])
        
        data=gdal.Open(inputRaster, GA_ReadOnly) 
        output=Workpath +InputDatafolder+ '_IA_.tif' #output file
        gdal.Translate(output,data,format='GTiff',options=translateOptions)
    else:
        #copy the config.txt for the speckle_filter processing
        source=inputRaster
        destination=Workpath +InputDatafolder+ '_IA_.tif'
        if not os.path.isfile(destination):
            shutil.copyfile(source, destination) 


#workstation='D:\\Data\\UAVSAR'
workstation='F:\\UAVSAR_NC'

#InputDatafolder='UA_neuser_32023_18067_000_180920_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18067_Cols'
#OutputDataFolder='UA_neuser_32023_18067_Processing'


#InputDatafolder='UA_neuser_32023_18068_000_180922_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18068_Cols'
#OutputDataFolder='UA_neuser_32023_18068_Processing'


#InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18069_Cols'
#OutputDataFolder='UA_neuser_32023_18069_Processing'


#InputDatafolderList=['UA_cpfear_13510_18065_008_180918_L090_CX_01']
InputDatafolderList=[
        'UA_cpfear_13510_18065_008_180918_L090_CX_01',
        'UA_cpfear_13510_18069_005_180923_L090_CX_01',
        'UA_cpfear_13510_18067_003_180920_L090_CX_01',
        'UA_cpfear_13510_18066_005_180919_L090_CX_01',
        'UA_cpfear_13510_18068_003_180922_L090_CX_01',
        
        'UA_cpfear_35303_18065_004_180918_L090_CX_01',
        'UA_cpfear_35303_18067_002_180920_L090_CX_01',
        'UA_cpfear_35303_18066_002_180919_L090_CX_01',
        'UA_cpfear_35303_18068_002_180922_L090_CX_01',
        'UA_cpfear_35303_18069_004_180923_L090_CX_01',
         
        'UA_lumber_31509_18066_006_180919_L090_CX_01',
        'UA_lumber_31509_18067_004_180920_L090_CX_01',
        'UA_lumber_31509_18069_006_180923_L090_CX_01',
        'UA_lumber_31509_18065_009_180918_L090_CX_01',
        'UA_lumber_31509_18068_004_180922_L090_CX_01'
        ]

#loop the daily SAR observation
for InputDatafolder in InputDatafolderList:

    os.chdir(workstation + '\\' + InputDatafolder)
#    for Paulifile in glob.glob("*pauli.tif"): 
#        PauliName=Paulifile
#        print(PauliName)
        
    GeoTiffOutputFolder=InputDatafolder[0:InputDatafolder.find('_00')+1] +'Cols'
    OutputDataFolder=InputDatafolder[0:InputDatafolder.find('_00')+1] + 'Processing'
    
    
    #begin to mask IA data
    _func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder)






