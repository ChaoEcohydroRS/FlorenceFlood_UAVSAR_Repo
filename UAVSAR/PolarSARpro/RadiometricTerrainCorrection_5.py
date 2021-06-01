# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 16:48:12 2019

@author: wayne
"""

#from metadata import metadata
import math
#from math import sqrt
import sys,os
sys.path.append(os.sys.path[0])
#import arcpy
import richdem as rd
import numpy as np
import glob
import rasterio
from osgeo import gdal
from rasterio.features import dataset_features
from rasterio.vrt import WarpedVRT
from shapely.geometry import shape, mapping
from calcSlopeDegrees_Revised import calcSlope
from calcSlopeDegrees_Revised import slopePython
from calcSlopeDegrees_Revised import getPixelSize

from rios import imagereader
from rios.imagewriter import ImageWriter

#Execute a python script in a specific directory
mydir = 'C:\\Users\\wayne\\OneDrive\\Documents\\Tools\\PythonScript\\UAVSAR'#os.getcwd() # would be the MAIN folder
mydir_tmp = mydir + "//PolarSARpro" # add the testA folder name
mydir_new = os.chdir(mydir_tmp) # change the current working directory
mydir = os.getcwd() # set the main directory again, now it calls testA

from create_header import create_INC_header 
from create_header import create_bin_header 
from ConvertHDR2Geotiff import load_ENVI_data
from ConvertHDR2Geotiff import array2raster

##------------------------------------------------------------
## Conversion functions to convert from/to dB
##------------------------------------------------------------

def CalculateSlopeDem(DEMfile,CalcSlopeFile,windowxsize,windowysize,OverlapSize,\
                                hDegree,zScale,minSlope):
    
    # Set up RIOS image reader
    reader = imagereader.ImageReader(DEMfile,\
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
    
        # Convert pixel sizes to m (if in degrees).
        xres, yres = info.getPixelSize()
        if hDegree:
            xSize, ySize = getPixelSize(yCoords, xres, yres)
        else:
            xSize = np.zeros_like(xCoords)
            ySize = np.zeros_like(yCoords)
            xSize[...] = xres
            ySize[...] = yres
    
        outBlock = calcSlope(inBlock, xSize, ySize, zScale, minSlope)
    
        # Check if writer exists, create one if not.
        if writer is None:
            writer = ImageWriter(CalcSlopeFile, info=info, firstblock=outBlock) 
        else:
            writer.write(outBlock)
    
    sys.stdout.write("\r 100 Percent Complete\n")
    
    calcStats = True
    
    if calcStats:
        # Close and calculate stats (for faster display)
        print("Writing stats...")
        writer.close(calcStats=True)
    else:
        writer.close(calcStats=False)
    print("Done")
    #return Slope Calculation State
    return 1



#Volumetric model (Hoekman & Reiche 2015)
#here this method just for ascending direction
#which need to be improved for the descending direction
def get_true_azimuth_direction(maskRasterObj):        

    #overview_level
    decim=1
    
    #with rasterio.open(s3_path) as src:
    with WarpedVRT(maskRasterObj, nodata=0) as vrt:
        feat = list(dataset_features(vrt, bidx=1, sampling=decim, band=False))[0]
                    
    #since the feat is so complex, we would like to simplify it 
    boundsgeometry = shape(feat["geometry"])
    feat["geometry"] = mapping(boundsgeometry.simplify(0.01))
    coords=feat["geometry"]['coordinates']
    
    #split the coords
    coordsList=list(coords[0])
    LonList = []
    LonList.append([e[0] for e in coordsList])
    
    LatList = []
    LatList.append([e[1] for e in coordsList])
    
    #get the lon and lat
    minLon=min(LonList[0])
    maxLon = max(LonList[0])
    
    minLat = min(LatList[0])
    maxLat = max(LatList[0])
    print(minLon,maxLon,minLat,maxLat)
    
    #get the true azimuth by geometry of the flightline
    trueAzimuth = \
    math.atan2(LatList[0][LonList[0].index(minLon)]-minLat, \
                (LonList[0][LatList[0].index(minLat)]-minLon))*(180.0/math.pi)+270.0
    
    #True azimuth across-range-look direction
    RangeLookDir=trueAzimuth-90.0
    return RangeLookDir

 
def VolumetricModel(maskfile,AspectFile,Slopefile,LIAfile,IAfile):    
    #take a raster path
    #returns an opened dataset object
    maskRasterObj = rasterio.open(maskfile)
    AspectRasterObj = rasterio.open(AspectFile)
    SlopeRasterObj = rasterio.open(Slopefile)
    #liaRasterObj = rasterio.open(LIAfile)
    IARasterObj= rasterio.open(IAfile)
    
    #get the data
#    maskRaster=maskRasterObj.read(1).astype(float)
    AspectRaster=AspectRasterObj.read(1).astype(float)
    SlopeRaster=SlopeRasterObj.read(1).astype(float)
    #liaRaster=liaRasterObj.read(1).astype(float)
    
    theta_iRad=IARasterObj.read(1).astype(float)
    # Article ( numbers relate to chapters)
    # 2.1.1 Radar geometry 
    #this should be incidence angle 
    #however, we don't have this raster layer
    #theta_i = IARaster
    
    #since this is good for incidence angle not lia
    #because the aspect of incidence angle is the range direction
    #phi_i = np.ma.masked_where(maskRaster > 0,\
    #        rd.TerrainAttribute(rd.rdarray(theta_i, no_data=np.nan),\
    #                            attrib='aspect')).mean()
    #therefore we can only get the rangeangle (phi-i) by flightline
    phi_i=get_true_azimuth_direction(maskRasterObj)
#    print(phi_i)
    
    # 2.1.2 Terrain geometry
    #calculate slope of the terrain, however, most of the cases,
    #the input DEM has a projection with horizontal unit of meter,
    #but here the DEM we have is in equal angle pixel cells 
    #thus here we just load the calculated slope data 
    #by custom defined slope calculation function
    #alpha_s = rd.TerrainAttribute(rd.rdarray(np.add(DEMRaster,39), no_data=np.nan), attrib='slope_degrees')
    alpha_s = SlopeRaster
    #since here the terrain package alsways calculated the downhill direction
    #however, here it requests to convert it to uphill direction by subtracting 180 degree
#    phi_s =np.add(rd.TerrainAttribute(rd.rdarray(DEMRaster, no_data=np.nan), attrib='aspect'),180)
    phi_s = AspectRaster
    # 2.1.3 Model geometry
    # reduce to 3 angle np.squeeze(phi_r, 0)
    #here the phi_i is not correct, should be revised by true range look
    phi_r = np.subtract(phi_i,phi_s)
#    print(np.shape(phi_r))

    
    # convert all to radians
    phi_rRad = phi_r*(math.pi/180)
    alpha_sRad = alpha_s*(math.pi/180)    
    ninetyRad = 90*(math.pi/180)
    
    #in many cases, the incidence angle was given
    #however, they don't provide it for UAVSAR
    #theta_iRad = theta_i#*(math.pi/180)
    
    # slope steepness in range (eq. 2) OK
    alpha_r = np.arctan(np.tan(alpha_sRad)*(np.cos(phi_rRad)))
    
    # slope steepness in azimuth (eq 3) OK
#    alpha_az = np.arctan(np.tan(alpha_sRad)*(np.sin(phi_rRad)))
    
    #derived the incidence angle based on local incidence angle OK
#    theta_iRad=np.arccos(np.cos(liaRaster)/np.cos(alpha_az))+alpha_r
    
    
    
#    out_meta=liaRasterObj.meta.copy()
#    outFile='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar.asfdaac.alaska.edu\\theta_i_calcued2.tif'
#    print('outFile:'+outFile)
#    with rasterio.open(outFile, "w", **out_meta) as dest:
#        dest.write(theta_i_calcued.astype(rasterio.float32),1)
    
    # Volumetric Model
#    nominator = np.tan(ninetyRad-theta_iRad+alpha_r)
#    denominator = np.tan(ninetyRad-theta_iRad)
#    volModel = np.absolute(nominator/denominator)
    volModel=np.absolute(np.tan(ninetyRad-theta_iRad+alpha_r)/np.tan(ninetyRad-theta_iRad))
    
    return theta_iRad,volModel#liaRaster,theta_iRad#

#
def applyVolModel(InputFile,liaRaster,volModel,outFile):
    #get the raster object
    TRasterObj = rasterio.open(InputFile)
    print('InputFile:'+InputFile)
    #get the matrix  
    TRaster=TRasterObj.read(1).astype(float)
    #T22Raster=T22RasterID.read(1).astype(float)
    #T33Raster=T33RasterID.read(1).astype(float)
    
    #were converted to sigma-naught
    # if the input is the sigma_naught in db then convert to natural
    #T_sigma=np.power(10,TRaster/10.0)#toNatural(T11Raster, maskRaster)
#    T_sigma=TRaster
    
    #gamma-naught
    #since this is a very flat area, 
    #the IncidenceAngle almost equare to lia
    T_gamma0=TRaster/(np.cos(liaRaster))
    
    # apply volModel
    gamma0_Volume = T_gamma0/volModel
    #convert to db
    #gamma0_VolumeDB =np.log10(gamma0_Volume)*10.0#*maskRaster
    
      
#    # Write it out as a geotiff
#    file_out="C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar.asfdaac.alaska.edu\\"+\
#    "Processing\\T3\\T11_gamma0_VolumeDB.tif"
    
    #get the geoinfo meta
    out_meta=TRasterObj.meta.copy()
    print('outFile:'+outFile)
    with rasterio.open(outFile, "w", **out_meta) as dest:
        dest.write(gamma0_Volume.astype(rasterio.float32))
    return 1


######################################################################
###############Users input parameters ###############
#####################################################################

workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar_experiment'

##---------------------------------------------------

#input folder of different observations

#InputDatafolder='UA_neuser_32023_18065_002_180918_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18065_Cols'
#OutputDataFolder='UA_neuser_32023_18065_Processing'

#InputDatafolder='UA_neuser_32023_18066_000_180919_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18066_Cols'
#OutputDataFolder='UA_neuser_32023_18066_Processing'

#InputDatafolder='UA_neuser_32023_18067_000_180920_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18067_Cols'
#OutputDataFolder='UA_neuser_32023_18067_Processing'

FirstTimeRunning=0
InputDatafolder='UA_neuser_32023_18068_000_180922_L090_CX_01'
GeoTiffOutputFolder='UA_neuser_32023_18068_Cols'
OutputDataFolder='UA_neuser_32023_18068_Processing'

#InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18069_Cols'
#OutputDataFolder='UA_neuser_32023_18069_Processing'

##---------------------------------------------------

DEMfile=workstation + '\\' + GeoTiffOutputFolder+\
"\\"+ InputDatafolder + "_hgt.tif"

LIAfile=workstation +'\\' + GeoTiffOutputFolder+\
"\\"+ InputDatafolder + "_inc.tif"

IAfile=workstation +'\\' + GeoTiffOutputFolder+\
"\\"+ InputDatafolder + "_IA.tif"

#set the output path
SlopeFile=workstation+'\\' + GeoTiffOutputFolder+\
"\\"+ InputDatafolder + "_slope.tif"

AspectFile=workstation+'\\' + GeoTiffOutputFolder+\
"\\"+ InputDatafolder + "_aspect.tif"

#set the folder for storing the terrain corrected files
Parameter_od_T3=workstation+"\\"+OutputDataFolder+"\\POC\\T3"


maskfile=Parameter_od_T3 + "\\" \
 "mask_valid_pixels.tif"

    
###----------------------------------------------
### End user Set Parameters
###-------------------------------------------------

# Empty lists to put information that will be recalled later.
grdFiles_List=[]
Lines_list = []
Samples_list = []


# Step 1: Look through folder and determine how many different flights there are
# by looking at the HDR files.
for file in os.listdir(workstation+'\\'+InputDatafolder):
    if file [-4:] == ".grd":
        grdFiles_List.append(file)
    if file [-4:] == ".ann":
        annFile=file
    if file [-4:] == ".inc":
        IncFiles=file
    if file [-4:] == ".hgt":
        hgtFile=file

#Step 2: Look through the annotation file.
# These can be in either .txt or .ann file types.   
#find the info we are interested in and append it to
# the appropriate list. We limit the variables to <=1 so that they only
# return two values (one for each polarization of
os.chdir(workstation+'\\'+InputDatafolder+'\\') #point to the dir
searchfile = open(annFile, "r") #read the ann file


#final_list = [float(x) for x in re.findall(match_number, s)]
#
for line in searchfile:
#    if "GRD Lines" in line:
    if "INC Lines" in line:
        Lines = [int(i) for i in line.split() if i.isdigit()][0]
#       Lines = line[55:60]
        if Lines not in Lines_list:
            Lines_list.append(Lines)

    elif "INC Samples" in line:
#                elif "GRD Samples" in line:
        Samples = [int(i) for i in line.split() if i.isdigit()][0]
#                    Samples = line[55:60]
        if Samples not in Samples_list:
            Samples_list.append(Samples)
            
#get the image height and width from annotation file
grd_rows=Lines_list[0]
grd_cols=Samples_list[0]



###----------------------------------------------
##derived the voluemetric Model
theta_iRad,volModel=VolumetricModel(maskfile,AspectFile,SlopeFile,LIAfile,IAfile)



###----------------------------------------------
##Apply the voluemetric Model to the 
#PolarimetricList=['T11','T22','T33','T12_real',\
#                 'T13_imag','T13_real','T23_imag','T23_real','T33']
#and then 
##convert the polarimetric variable to geotiff format for uploading
###--------------------------------------------------------
#get all input
T3_Matrix_Dir=Parameter_od_T3
T3_Matrix_List=[]

#get all elements of the T3 matrix as a list to be applied
os.chdir(T3_Matrix_Dir)
for file in glob.glob("T*.bin"):
    T3_Matrix_List.append(file)
    
#begin to conduct the operation on each T3 maxtrix element
for T3CMRasterName in T3_Matrix_List:
    
    #apply the terrain correction
    #open the original binary image and read the basic infomation
    T3CMRasterObj = rasterio.open(T3_Matrix_Dir + '\\' + T3CMRasterName ,driver='ENVI')
    
    #get the meta info from source file
    Source_meta=T3CMRasterObj.meta.copy()
    
    #update the meta
    Source_meta.update(
        driver='GTiff',
        dtype=rasterio.float32,
        compress='lzw')
    
    print('Updated Source_meta',Source_meta)
    
    
    
    #now the data are just original sigma data?
    T3CMRaster=T3CMRasterObj.read(1).astype(float)
    
    ###----------------apply volModel--------------------------
    #gamma-naught
    #it should be the incidence angle
    #since this is a very flat area, 
    #the IncidenceAngle almost equare to lia
    #be careful of the nan value since the divide or arccos calculations 
    #may encountered some invalid value
    T3CM_gamma0=np.nan_to_num(T3CMRaster/(np.cos(theta_iRad))/volModel)
                
    #and then save the polarimetric variable as geotiff format for uploading
    # get the export file name token
    dataVar=os.path.splitext(os.path.basename(T3CMRasterName))[0]
    # the output file
    file_out=workstation+'\\'+GeoTiffOutputFolder+'\\UA_'+\
    os.path.splitext(os.path.basename(IncFiles))[0]+"_"+dataVar+".tif"

    # Write it out as a geotiff    
    with rasterio.open(file_out, "w", **Source_meta) as dest:
        dest.write(T3CM_gamma0.astype(rasterio.float32),1)
        


    
##############################
###----------Code Backup------------------------------------ 

#
####----------------------------------------------
###-------stop use it since it is so slow and take lots of time
###--------------------------------------------------------

#####Calculate slope of the terrain
##if the DEM has a projection with horizontal unit of meter, 
##just set the parameter of hDegree as False
##most of the cases,the input DEM has a projection with horizontal unit of meter,
##but here the DEM we have is in equal angle pixel cells 
#'''
#Note: this process is very slow regarding to the large raster data
#thus, it's better to run once and save the results out
#'''
#

#
#if FirstTimeRunning==1:
#    #the size of overlap window
#    OverlapSize=3
#    
#    windowxsize=int(grd_cols/5)#20788#2048
#    
#    windowysize=int(grd_rows/5)#19504#2048
#    
#    zScale=1
#    
#    #args.spacing_degrees
#    hDegree = True
#    
#    minSlope=None
#    SlopeCalState=CalculateSlopeDem(DEMfile,SlopeFile,windowxsize,windowysize,OverlapSize,
#                            hDegree,zScale,minSlope)
#    
#elif FirstTimeRunning==0:
#    SlopeFile=SlopeFile
#        
        


#
####----------------------------------------------





