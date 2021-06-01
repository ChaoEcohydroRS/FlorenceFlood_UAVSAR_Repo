# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 20:12:37 2020

@author: wayne
"""


import os
import subprocess
import glob
import shutil
    
#######################################################################
################Users input parameters ###############
######################################################################
#
#workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar_experiment'
#
#workstation='D:\\Data\\UAVSAR'
#
##input
#InputDatafolder='UA_neuser_32023_18065_002_180918_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18065_Cols'
#OutputDataFolder='UA_neuser_32023_18065_Processing'
#
##InputDatafolder='UA_neuser_32023_18066_000_180919_L090_CX_01'
##GeoTiffOutputFolder='UA_neuser_32023_18066_Cols'
##OutputDataFolder='UA_neuser_32023_18066_Processing'
#
##InputDatafolder='UA_neuser_32023_18067_000_180920_L090_CX_01'
##GeoTiffOutputFolder='UA_neuser_32023_18067_Cols'
##OutputDataFolder='UA_neuser_32023_18067_Processing'
#
##InputDatafolder='UA_neuser_32023_18068_000_180922_L090_CX_01'
##GeoTiffOutputFolder='UA_neuser_32023_18068_Cols'
##OutputDataFolder='UA_neuser_32023_18068_Processing'
#
##InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
##GeoTiffOutputFolder='UA_neuser_32023_18069_Cols'
##OutputDataFolder='UA_neuser_32023_18069_Processing'
    
    
def _func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder):    
    ######################################################################
    ########Process polarimetric data in PolSARpro environment###############
    #####################################################################
    
    os.chdir(workstation+'\\'+InputDatafolder+'\\')
    
    softDir='C:\\Program Files\\PolSARpro_v6.0_Biomass_Edition\\Soft\\bin\\'
    
    
    
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
#        if file [-4:] == ".inc":
#            IncFiles=file
#        if file [-4:] == ".hgt":
#            hgtFile=file
    
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
    
#    Parameter_hf=workstation+'\\'+InputDatafolder+'\\'+annotationFileName
#    Parameter_id=workstation+"\\"+InputDatafolder 
    Parameter_od_SMS=workstation+"\\" + OutputDataFolder + "\\SMS"
    if not os.path.exists(Parameter_od_SMS):
        os.makedirs(Parameter_od_SMS)
    
    #set output path and folder
    #C:\Workstation\NC_Study\UAVSAR\Data\uavsar_experiment\UA_neuser_32023_18068_Processing\POC
    Parameter_od_T3=workstation+"\\"+OutputDataFolder+"\\SpeckleFilter\\T3"
#    Parameter_od_T3=workstation+"\\"+OutputDataFolder+"\\POC\\T3"
    #Parameter_Scatter_Segmentation_od=workstation+"/"+OutputDataFolder+"/ScatterSegementation/T3"
    
    if not os.path.exists(Parameter_od_T3):
        os.makedirs(Parameter_od_T3)
        
    #if not os.path.exists(Parameter_Scatter_Segmentation_od):
    #    os.makedirs(Parameter_Scatter_Segmentation_od)    
    
    #Freeman_Odd，Freeman_Dbl，Freeman_Vol
    DecompsNormFolder=workstation+"\\"+OutputDataFolder+"\\DecompsNorm"
    
    Parameter_Freeman_Odd_File=DecompsNormFolder+'\\Freeman_Odd.bin'
    
    Parameter_Freeman_Dbl_File=DecompsNormFolder+'\\Freeman_Dbl.bin'
    
    Parameter_Freeman_Vol_File=DecompsNormFolder+'\\Freeman_Vol.bin'
    
    #
    Parameter_errf="C:\\Users\\wayne\\AppData\\Local\\Temp\\PolSARpro-Bio_6.0.1\\Tmp\\MemoryAllocError.txt"
    Parameter_cms= "C:\\Users\\wayne\\AppData\\Roaming\\PolSARpro-Bio_6.0.1\\ColorMap\\ColorMap_BLUE.pal" 
    Parameter_cmd= "C:\\Users\\wayne\\AppData\\Roaming\\PolSARpro-Bio_6.0.1\\ColorMap\\ColorMap_SPRING.pal" 
    Parameter_cmr= "C:\\Users\\wayne\\AppData\\Roaming\\PolSARpro-Bio_6.0.1\\ColorMap\\ColorMap_SUMMER.pal"  
    Parameter_clm= "C:\\Users\\wayne\\AppData\\Roaming\\PolSARpro-Bio_6.0.1\\ColorMap\\Planes_H_Alpha_Lambda_ColorMap27.pal" 
    
    ######################################################################
    ##### Pauli, H/A/Alpha and Freeman-Durden decompositions
    ######################################################################
    
    ######################################
    #lee_scattering_model_based_classification
    ######################################
    
    #Function Soft/bin/data_process_sngl/lee_scattering_model_based_classification.exe
    #Arguments: -id "C:/Workstation/POC/T3" 
    #-od "C:/Workstation/POC/T3" 
    #-isf "C:/Workstation/Freeman/Freeman_Odd.bin" 
    #-idf "C:/Workstation/Freeman/Freeman_Dbl.bin" 
    #-irf "C:/Workstation/Freeman/Freeman_Vol.bin" 
    #-iodf T3 -nwr 3 -nwc 3 -ofr 0 -ofc 0 -fnr 19552 -fnc 20837 
    #-pct 10 -nit 10 -bmp 1 -ncl 30 -mct 0.5 -fscn 3 -fdcn 3 -fvcn 3 
    #-cms "C:/Users/wayne/AppData/Roaming/PolSARpro-Bio_6.0.1/ColorMap/ColorMap_BLUE.pal" 
    #-cmd "C:/Users/wayne/AppData/Roaming/PolSARpro-Bio_6.0.1/ColorMap/ColorMap_SPRING.pal" 
    #-cmr "C:/Users/wayne/AppData/Roaming/PolSARpro-Bio_6.0.1/ColorMap/ColorMap_SUMMER.pal"  
    #-errf "C:/Users/wayne/AppData/Local/Temp/PolSARpro-Bio_6.0.1/Tmp/MemoryAllocError.txt" 
    #-mask "C:/Workstation/POC/T3/mask_valid_pixels.bin"
    
    #Parameters:
    # (string)       -id     input directory
    # (string)       -od     output directory
    # (string)       -iodf   input-output data format
    # (int)          -nwr    Nwin Row
    # (int)          -nwc    Nwin Col
    # (int)          -ofr    Offset Row
    # (int)          -ofc    Offset Col
    #
    #"-fscn 6 -fdcn 4 -fvcn 3" + \
    
    try:
        ExcludeProgram=softDir+'data_process_sngl\\'+'lee_scattering_model_based_classification.exe'
        subprocess.call(ExcludeProgram + " -id \"" + Parameter_od_T3 + \
                                     "\" -od \"" + Parameter_od_SMS + \
                                     "\" -isf \"" + Parameter_Freeman_Odd_File + \
                                     "\" -idf \"" + Parameter_Freeman_Dbl_File + \
                                     "\" -irf \"" + Parameter_Freeman_Vol_File + \
                                     "\" -iodf T3 -nwr 3 -nwc 3 -ofr 0 -ofc 0 -fnr "+ \
                                     str(grd_rows) + " -fnc " + str(grd_cols) + \
                                     " -pct 10 -nit 10 -bmp 1 -ncl 30 -mct 0.5 "+\
                                     "-fscn 9 -fdcn 4 -fvcn 3" + \
                                     " -cms \""+Parameter_cms + \
                                     "\"  -cmd \""+Parameter_cmd + \
                                     "\"  -cmr \""+Parameter_cmr + \
                                     "\"  -errf \""+ Parameter_errf + \
                                     "\" -mask \""+ Parameter_od_T3 + \
                                     "\\mask_valid_pixels.bin" + "\"")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("scattering model based command '{}' "+\
                           "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
    
    
    #
    #Function 
    #Soft/bin/data_process_sngl/h_alpha_lambda_planes_classifier.exe
    #Arguments: 
    #-id "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18068_Processing/POC/T3" 
    #-od "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18068_Processing/POC/T3" 
    #-ofr 0 -ofc 0 -fnr 19552 -fnc 20837 
    #-clm "C:/Users/wayne/AppData/Roaming/PolSARpro-Bio_6.0.1/ColorMap/Planes_H_Alpha_Lambda_ColorMap27.pal"  
    #-errf "C:/Users/wayne/AppData/Local/Temp/PolSARpro-Bio_6.0.1/Tmp/MemoryAllocError.txt" 
    #-mask "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18068_Processing/POC/T3/mask_valid_pixels.bin"
    
    #try:
    #    ExcludeProgram=softDir+'data_process_sngl\\'+'h_alpha_lambda_planes_classifier.exe'
    #    subprocess.call(ExcludeProgram + " -id \"" + Parameter_od_T3 + \
    #                                 "\" -od \"" + Parameter_od_T3 + \
    #                                 "\" -ofr 0 -ofc 0 -fnr "+ \
    #                                 str(grd_rows) + " -fnc " + str(grd_cols) + \
    #                                 " -clm \""+Parameter_clm + \
    #                                 "\"  -errf \""+ Parameter_errf + \
    #                                 "\" -mask \""+ Parameter_od_T3 + \
    #                                 "\\mask_valid_pixels.bin" + "\"")
    #except subprocess.CalledProcessError as e:
    #    raise RuntimeError("h_alpha_lambda_planes command '{}' "+\
    #                       "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    #
