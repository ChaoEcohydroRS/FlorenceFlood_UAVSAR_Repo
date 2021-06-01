# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 10:47:01 2020

@author: wayne
"""

#from metadata import metadata
import math
import csv
import pandas
#from math import sqrt
import sys,os
sys.path.append(os.sys.path[0])
#import arcpy
import richdem as rd
import numpy as np
import glob
import rasterio
from osgeo import gdal,ogr,osr
import osgeo.gdalnumeric as gdn
from rasterio.features import dataset_features
from rasterio.vrt import WarpedVRT
from shapely.geometry import shape, mapping
from calcSlopeDegrees_Revised import calcSlope
from calcSlopeDegrees_Revised import slopePython
from calcSlopeDegrees_Revised import getPixelSize

from rios import imagereader
from rios.imagewriter import ImageWriter
import ee

#Execute a python script in a specific directory
mydir = 'C:\\Users\\wayne\\OneDrive\\Documents\\Tools\\PythonScript\\UAVSAR'#os.getcwd() # would be the MAIN folder
mydir_tmp = mydir + "//PolarSARpro" # add the testA folder name
mydir_new = os.chdir(mydir_tmp) # change the current working directory
mydir = os.getcwd() # set the main directory again, now it calls testA

from create_header import create_INC_header 
from create_header import create_bin_header 
from ConvertHDR2Geotiff import load_ENVI_data
from ConvertHDR2Geotiff import array2raster


###------------------------------
###-------apply the incidence angle correction (normalization)
def applyNormaliziedModel(InputFile,IARaster,EachLinSlopeValue):
    #get the raster object
    T3RasterObj = rasterio.open(InputFile)
    
    #get the meta info from source file
    Source_meta=T3RasterObj.meta.copy()
    
    #get the matrix  
    T3Raster=T3RasterObj.read(1).astype(float)
    
    ###----------------apply volModel--------------------------
    #gamma-naught
    #it should be the incidence angle
    #since this is a very flat area, 
    #the IncidenceAngle almost equare to lia
    #be careful of the nan value since the divide or arccos calculations 
    #may encountered some invalid value
    #T3CM_gamma0=np.nan_to_num(T3CMRaster/(np.cos(theta_iRad))/volModel)
    

    # apply normalization model
    #var T11_gamma02_n2=T11_sigma
    #.divide(theta_i_true.multiply(Math.PI/180).pow(ee.Image.constant(LinSlope)))
    #T3_gamma0=T3Raster/(np.cos(IARaster))
    #T3CM_gamma0=np.nan_to_num(T3CMRaster/(np.cos(theta_iRad))/volModel)
    #90*(math.pi/180)
    #volModel=np.absolute(np.tan(ninetyRad-theta_iRad+alpha_r)/np.tan(ninetyRad-theta_iRad))
    #T3_gamma0=T3Raster/np.power(np.multiply(IARaster, math.pi/180),EachLinSlopeValue)
    #since the IA is in rad angle not degree angle
    #sometime the IA has inconsistent row as the T3
    #remove the last row from IA by 
    if (IARaster.shape[0]+1) == T3Raster.shape[0]:
        IARaster=np.delete(IARaster, IARaster.shape[0]-1, 0)
    T3_gamma0=T3Raster/np.power(IARaster,EachLinSlopeValue)
    
    # Retrun the metadate and the corrected T3  
    return Source_meta,T3_gamma0

# open gdal raster dataset for writing
def writeRasterIntoEnvi(geoInputFile,rasterImg,file_out,driver):
    
    # 
    GeoImg = gdal.Open(geoInputFile)
    outraster1 = gdal.GetDriverByName(driver).Create(
            file_out,                                     # output ENVI
            GeoImg.RasterXSize,                                # number of columns
            GeoImg.RasterYSize,                                # number of rows
            1 ,                                             # number of bands
            gdal.GDT_Float32)                               # data type
    
    # set geotransform and projection information
    geo = GeoImg.GetGeoTransform()                         # get geotransform from input raster
    outraster1.SetGeoTransform(geo)                     # set geotransform
    wkt = GeoImg.GetProjection()                           # get projection from input raster
    outraster1.SetProjection(wkt)                       # set projection 
    
    # get band 1
    outraster1b = outraster1.GetRasterBand(1)           # get band 1 of output
    
    # write to band 1
    outraster1b.WriteArray(rasterImg)                  # write savi array to band 1
    
    outraster1.FlushCache()                             # write out
    outraster1 = None
    
    
def _func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder):
    ######################################################################
    ###############Users input parameters ###############
    #####################################################################
    
#    workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar_experiment'
#    
#    workstation='D:\\Data\\UAVSAR'
#    ##---------------------------------------------------
#    
#    #input folder of different observations
#    
#    InputDatafolder='UA_neuser_32023_18065_002_180918_L090_CX_01'
#    GeoTiffOutputFolder='UA_neuser_32023_18065_Cols'
#    OutputDataFolder='UA_neuser_32023_18065_Processing'
    
    #InputDatafolder='UA_neuser_32023_18066_000_180919_L090_CX_01'
    #GeoTiffOutputFolder='UA_neuser_32023_18066_Cols'
    #OutputDataFolder='UA_neuser_32023_18066_Processing'
    
    #InputDatafolder='UA_neuser_32023_18067_000_180920_L090_CX_01'
    #GeoTiffOutputFolder='UA_neuser_32023_18067_Cols'
    #OutputDataFolder='UA_neuser_32023_18067_Processing'
    
    #FirstTimeRunning=0
    #InputDatafolder='UA_neuser_32023_18068_000_180922_L090_CX_01'
    #GeoTiffOutputFolder='UA_neuser_32023_18068_Cols'
    #OutputDataFolder='UA_neuser_32023_18068_Processing'
    
    #InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
    #GeoTiffOutputFolder='UA_neuser_32023_18069_Cols'
    #OutputDataFolder='UA_neuser_32023_18069_Processing'
    
    ##---------------------------------------------------
    
    DEMfile=workstation + '\\' + GeoTiffOutputFolder+\
    "\\"+ InputDatafolder + "_hgt.tif"
    
    #LIAfile=workstation +'\\' + GeoTiffOutputFolder+\
    #"\\"+ InputDatafolder + "_inc.tif"
    
    IAfile=workstation +'\\' + GeoTiffOutputFolder+\
    "\\"+ InputDatafolder + "_IA_.tif"
    
    #set the output path
    SlopeFile=workstation+'\\' + GeoTiffOutputFolder+\
    "\\"+ InputDatafolder + "_slope.tif"
    
    AspectFile=workstation+'\\' + GeoTiffOutputFolder+\
    "\\"+ InputDatafolder + "_aspect.tif"
    
    #set the folder for storing geotiff files
    #C:\Workstation\NC_Study\UAVSAR\Data\uavsar_experiment\UA_neuser_32023_18068_Cols
    Parameter_od_T3=workstation+"\\"+GeoTiffOutputFolder
    
    #maskfile=Parameter_od_T3 + "\\" \
    # "mask_valid_pixels.tif"
    
    #downloaded csv file (orgnized manully) for normalization correction
    #UA_neuser_32023_18068_ColsRadNormFactors.csv
#    csvfile=workstation + '\\' + GeoTiffOutputFolder+\
#    "\\"+ GeoTiffOutputFolder + "RadNormFactors.csv"
    RadNormFactorsCsvfile='C:\\Users\\wayne\\Google Drive\\SolarPV\\'+ \
    GeoTiffOutputFolder+'RadNormFactors.csv'
    
    ###----------------------------------------------
    ### End user Set Parameters
    ###-------------------------------------------------
    
    ###-----------------------
    ###-------read normalization parameters--------
    #read the csv to get the normalization correction parameters
    #get slope and intecept of the fitted linear regression model
    #LinSlope=ee.Array(linearRegsCoeff.get('coefficients')).get([1, 0]);
    #print('LinSlope',LinSlope);
    
    #read csv file as a dataframe
    LinearSlopeDataFrame = pandas.read_csv(RadNormFactorsCsvfile)
    
    ###----------------------------------------------
    #load IA raster
    IARasterObj = rasterio.open(IAfile)
    IARaster=IARasterObj.read(1).astype(float)
    
    ##Apply the normalization model to the 
    ##the H_A_Alpha list to be applied
    #H_A_Alpha_List=['alpha','anisotropy','entropy','lambda']
    #
    ##the Freeman list to be applied
    #Freeman_List=['Freeman_Dbl','Freeman_Odd','Freeman_Vol']
    
    #and then save them as bin for segementation
    ###--------------------------------------------------------
    #get all input
    DecompositedGeotiff_Dir=Parameter_od_T3
    DecompositeGeotiff_List=[]
    
    #get all elements of the D matrix as a list to be applied
    os.chdir(DecompositedGeotiff_Dir)
    for file in glob.glob("*D_*.tif"):
        DecompositeGeotiff_List.append(file)
    
    #filter pauli decomposition var
    DecompositeGeotiff_List_Filtered=[element for element in DecompositeGeotiff_List if 'D_pauli' not in element]
    print('DecompositeGeotiff_List_Filtered',DecompositeGeotiff_List_Filtered)
    
    #further filter the list required to correction
    DecompositeGeotiff_List_Filtered=[element for element in DecompositeGeotiff_List_Filtered if 'D_Freeman' in element]
    
    #begin to conduct the operation on each T3 maxtrix element
    for DecompositedRasterName in DecompositeGeotiff_List_Filtered:
        
        #and then save the polarimetric variable as geotiff format for uploading
        # get the export file name token
        dataVar=os.path.splitext(os.path.basename(DecompositedRasterName))[0]
        
        
        #the radiometric as input
        InputFile=DecompositedGeotiff_Dir + '\\' + DecompositedRasterName
            
        #get the target row based on a column value from the csv dataframe
        #which is the corresponding LinSlope
        #UA_neuser_32023_18068_000_180922_L090_CX_01_D_entropy
        CorrespondingLinSlope=LinearSlopeDataFrame.loc[LinearSlopeDataFrame['VarName'] ==
                                       dataVar.split("_01_",1)[1]].LinearSlope.values[0]
            
        #apply the radiometric normalization correction
        Source_meta,CorrDecompositedRaster=applyNormaliziedModel(InputFile,IARaster,CorrespondingLinSlope)
        
        #update the meta
        Source_meta.update(
            driver='GTiff',
            dtype=rasterio.float32,
            compress='lzw')
                
        # the output file
        outNormDir=workstation+'\\'+OutputDataFolder+'\\DecompsNorm\\'
        if not os.path.exists(outNormDir):
            os.makedirs(outNormDir)
            
        file_out=outNormDir+dataVar.split("_D_",1)[1] +".bin"
    
    #    # Write it out as a bin for scattering model based segementation    
    #    with rasterio.open(file_out, "w", **Source_meta) as dest:
    #        dest.write(CorrDecompositedRaster.astype(rasterio.float32),1)
        
        writeRasterIntoEnvi(InputFile,CorrDecompositedRaster,file_out,'ENVI')
            

#workstation='D:\\Data\\UAVSAR'
#InputDatafolder='UA_neuser_32023_18067_000_180920_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18067_Cols'
#OutputDataFolder='UA_neuser_32023_18067_Processing'
#
#
#_func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder)


