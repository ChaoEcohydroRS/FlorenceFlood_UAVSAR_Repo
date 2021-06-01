# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 12:15:46 2020

@author: wayne
"""
import os
import subprocess
import glob
import shutil
import time



    
#########################################
#InputDatafolder='UA_neuser_32023_18068_000_180922_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18068_Cols'
#OutputDataFolder='UA_neuser_32023_18068_Processing'

def _func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder):    
    #earthengine --no-use_cloud_api upload image 
    #--asset_id=projects/GlobalReservoirs/UAVSAR/UA_neuser_32023_18065_Cols/UA_neuser_32023_18065_002_180918_L090_CX_01_inc 
    #--pyramiding_policy=sample gs://aviris_ng/UA_neuser_32023_18065_002_180918_L090_CX_01_inc.tif 
    
    rasterGeotiff_List=[]
    
    rasterGeotiff_Dir=workstation + '\\' + GeoTiffOutputFolder
    
    
    os.chdir(rasterGeotiff_Dir)
    
    ##get all elements of the D matrix as a list to be applied
    for file in glob.glob("*.tif"):
#    for file in glob.glob("*_P_*.tif"):
        rasterGeotiff_List.append(file)
    
#    #filter pauli decomposition var
#    Geotiff_List_Filtered=[element for element in rasterGeotiff_List if 'D_pauli' not in element]
    
    #begin to conduct the operation on each T3 maxtrix element
    for rasterFileName in rasterGeotiff_List:
        #get the basename of the raster file
        baseName=os.path.splitext(os.path.basename(rasterFileName))[0]
        
        #set the property name based on raster file name
        propertyName=baseName.split("_01_",1)[1]
        
        
        try:
            ExcludeProgram='earthengine'+ \
            ' asset set -p "(string)name='+propertyName+'" '+\
            ' projects/GlobalReservoirs/UAVSAR/'+GeoTiffOutputFolder+'/'+\
            baseName
            print(ExcludeProgram)
            
            subprocess.call(ExcludeProgram)
            time.sleep(3)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("earthengine asset name  command '{}' "+\
                               "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            
            
#workstation='D:\\Data\\UAVSAR'
##workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar_experiment'
#
##InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
##GeoTiffOutputFolder='UA_neuser_32023_18069_Cols'
##OutputDataFolder='UA_neuser_32023_18069_Processing'
#
##InputDatafolder='UA_neuser_32023_18065_002_180918_L090_CX_01'
##GeoTiffOutputFolder='UA_neuser_32023_18065_Cols'
##OutputDataFolder='UA_neuser_32023_18065_Processing'
#
#
#InputDatafolder='UA_neuser_32023_18066_000_180919_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18066_Cols'
#OutputDataFolder='UA_neuser_32023_18066_Processing'
##    
#
##InputDatafolder='UA_neuser_32023_18067_000_180920_L090_CX_01'
##GeoTiffOutputFolder='UA_neuser_32023_18067_Cols'
##OutputDataFolder='UA_neuser_32023_18067_Processing'
#
##InputDatafolder='UA_neuser_32023_18068_000_180922_L090_CX_01'
##GeoTiffOutputFolder='UA_neuser_32023_18068_Cols'
##OutputDataFolder='UA_neuser_32023_18068_Processing'
#
#
#_func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder)


