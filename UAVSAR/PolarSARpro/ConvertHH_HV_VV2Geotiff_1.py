# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 23:43:21 2020

@author: wayne
"""

import os
import subprocess
import glob
import shutil

#Execute a python script in a specific directory
mydir = 'C:\\Users\\wayne\\OneDrive\\Documents\\Tools\\PythonScript\\UAVSAR'#os.getcwd() # would be the MAIN folder
mydir_tmp = mydir + "\\PolarSARpro" # add the testA folder name
mydir_new = os.chdir(mydir_tmp) # change the current working directory
mydir = os.getcwd() # set the main directory again, now it calls testA

from create_header import create_INC_header 
from create_header import create_bin_header
from create_header import create_grd_header 
from ConvertHDR2Geotiff import load_ENVI_data
from ConvertHDR2Geotiff import load_BMP_data
from ConvertHDR2Geotiff import array2raster



######################################################################
###############Users input parameters ###############
#####################################################################

#workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar_experiment'
#
#
#workstation='D:\\Data\\UAVSAR'
#
##input
#InputDatafolder='UA_neuser_32023_18065_002_180918_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18065_Cols'
#OutputDataFolder='UA_neuser_32023_18065_Processing'

#InputDatafolder='UA_neuser_32023_18066_000_180919_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18066_Cols'
#OutputDataFolder='UA_neuser_32023_18066_Processing'

#InputDatafolder='UA_neuser_32023_18067_000_180920_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18067_Cols'
#OutputDataFolder='UA_neuser_32023_18067_Processing'

#InputDatafolder='UA_neuser_32023_18068_000_180922_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18068_Cols'
#OutputDataFolder='UA_neuser_32023_18068_Processing'

#InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18069_Cols'
#OutputDataFolder='UA_neuser_32023_18069_Processing'

def _func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder):
    
    ######################################################################
    ###############Using PolSARPRO extract data###############
    #####################################################################
    
    os.chdir(workstation+'\\'+InputDatafolder+'\\')
    
    # Empty lists to put information that will be recalled later.
    grdFiles_List=[]
    Lines_list = []
    Samples_list = []
    Latitude_list = []
    Longitude_list = []
    Files_list = []
    
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
    
    
    #annotation_file
    annotationFileName=os.path.basename(annFile) #'neuser_32023_18067_000_180920_L090_CX_01.ann'
    
    Parameter_id=workstation+"/"+InputDatafolder+"/" 
    
    
    
    ######################################################################
    ########Create hdr for decomposition bin files###########
    #####################################################################
    
    Parameter_Decomps_In=workstation+"/"+OutputDataFolder
    
    #set output path and folder
    Parameter_Decomps_od=workstation+"/"+GeoTiffOutputFolder
    
    annfolder=Parameter_id
    
#    #create Freeman hdr file
#    create_bin_header(Parameter_Decomps_In+'/Freeman',annfolder)
#    
#    #create H/Alpha/A matrix hdr
#    create_bin_header(Parameter_Decomps_In+'/H_A_Alpha',annfolder)
    
    #create HH, HV, and VV grd matrix hdr
    Parameter_HH_HV_VV_List=['HHHH','HVHV','VVVV']
    create_grd_header(Parameter_id,annfolder)
    
    
    ####################################################################
    #the polarization list to be applied: HH, HV, VV
    for polarizationName in Parameter_HH_HV_VV_List:
        dataVar=polarizationName
        os.chdir(Parameter_id)
        for file in glob.glob("*" + dataVar + "*.grd"):
            ## Open grd data 
            file_name=Parameter_id + '\\' + file
            data, geodata = load_ENVI_data(file_name)
        
            # Write it out as a geotiff
            file_out=Parameter_Decomps_od+'\\'+InputDatafolder+"_P_"+dataVar+".tif"
            array2raster(data, geodata, file_out, gdal_driver='GTiff')



#workstation='D:\\Data\\UAVSAR'
##InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
##GeoTiffOutputFolder='UA_neuser_32023_18069_Cols'
##OutputDataFolder='UA_neuser_32023_18069_Processing'
#
#
#InputDatafolder='UA_neuser_32023_18065_002_180918_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18065_Cols'
#OutputDataFolder='UA_neuser_32023_18065_Processing'
#
#_func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder)


############## Backup #################################
            
    #######################################################################
    #########Convert to geotiff (bin files) ###########
    ######################################################################
    
    
#    ####################################################################
#    #the H_A_Alpha list to be applied
#    H_A_Alpha_List=['alpha','anisotropy','entropy','lambda']
#    
#    for T3CMRasterName in H_A_Alpha_List:
#        dataVar=T3CMRasterName
#        
#        ## Open some data inc /neuser_32023_18067_000_180920_L090_CX_01.hgt
#        file_name=Parameter_Decomps_In+'/H_A_Alpha/'+dataVar+".bin"
#        data, geodata = load_ENVI_data(file_name)
#        
#        # Write it out as a geotiff
#        file_out=Parameter_Decomps_od+'\\'+InputDatafolder+"_D_"+dataVar+".tif"
#        array2raster(data, geodata, file_out, gdal_driver='GTiff') 
#        
#        
#    ####################################################################
#    #the Freeman list to be applied
#    Freeman_List=['Freeman_Dbl','Freeman_Odd','Freeman_Vol']
#    
#    for T3CMRasterName in Freeman_List:
#        dataVar=T3CMRasterName
#        
#        ## Open some data inc /neuser_32023_18067_000_180920_L090_CX_01.hgt
#        file_name=Parameter_Decomps_In+'/Freeman/'+dataVar+".bin"
#        data, geodata = load_ENVI_data(file_name)
#        
#        # Write it out as a geotiff
#        file_out=Parameter_Decomps_od+'\\'+InputDatafolder+"_D_"+dataVar+".tif"
#        array2raster(data, geodata, file_out, gdal_driver='GTiff')
    
    #
    #####################################################################
    ######Convert the Scattering model-based segmentation bin to tiff###
    ##################################################################### 
    ##the Scattering model-based segmentation to be applied
    #Segmentation_List=['scattering_model_based_classification_3x3']
    #
    #Parameter_Segmentation_od=workstation+"/"+OutputDataFolder+"/ScatterSegementation"
    #
    #for T3CMRasterName in Segmentation_List:
    #    dataVar=T3CMRasterName
    #    
    #    ## Open some data inc /neuser_32023_18067_000_180920_L090_CX_01.hgt
    #    file_name=Parameter_Segmentation_od+'/'+dataVar+".bin"
    #    data, geodata = load_ENVI_data(file_name)
    #    
    #    # Write it out as a geotiff
    #    # SMBS, Scattering Model-based Segmentation
    #    file_out=Parameter_Segmentation_od+'\\'+InputDatafolder+"_S_SMS.tif"
    #    array2raster(data, geodata, file_out, gdal_driver='GTiff') 
    # 

    