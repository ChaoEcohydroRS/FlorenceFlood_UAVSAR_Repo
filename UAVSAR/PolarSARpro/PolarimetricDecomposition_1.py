# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 12:48:55 2020
To process polarimetric decompositions and segmentation in the PolSARpro environment
 
@author: chao wang | chao.wang@unc.edu
supported by Tamlin M. Pavelsky

"""

import os
import subprocess
import glob
import shutil



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
    
    Parameter_hf=workstation+'\\'+InputDatafolder+'\\'+annotationFileName
    Parameter_id=workstation+"\\"+InputDatafolder 
    Parameter_od=workstation+"\\"+InputDatafolder
    
    #set output path and folder
    #C:\Workstation\NC_Study\UAVSAR\Data\uavsar_experiment\UA_neuser_32023_18068_Processing\POC
#    Parameter_od_T3=workstation+"\\"+OutputDataFolder+"\\POC\\T3"
    #since POC always have unknown error, I just comment it
    Parameter_od_T3=workstation+"\\"+OutputDataFolder+"\\SpeckleFilter\\T3"
#    Parameter_Pauli_od=workstation+"/"+OutputDataFolder+"\\Pauli"
    Parameter_H_A_Alpha_od=workstation+"\\"+OutputDataFolder+"\\H_A_Alpha"
    Parameter_Freeman_od=workstation+"\\"+OutputDataFolder+"\\Freeman"
    
    if not os.path.exists(Parameter_od_T3):
        os.makedirs(Parameter_od_T3)
        
#    if not os.path.exists(Parameter_Pauli_od):
#        os.makedirs(Parameter_Pauli_od)
        
    if not os.path.exists(Parameter_H_A_Alpha_od):
        os.makedirs(Parameter_H_A_Alpha_od)
        
    if not os.path.exists(Parameter_Freeman_od):
        os.makedirs(Parameter_Freeman_od)    
        
    Parameter_errf="C:/Users/wayne/AppData/Local/Temp/PolSARpro-Bio_6.0.1/Tmp/MemoryAllocError.txt"
    Parameter_Configf="C:/Users/wayne/AppData/Local/Temp/PolSARpro-Bio_6.0.1/Tmp/2019_11_02_21_46_42_uavsar_config.txt"
#    Parameter_Pauli_of=Parameter_Pauli_od+"/PauliRGB.bmp"
    
    ######################################################################
    ##### Pauli, H/A/Alpha and Freeman-Durden decompositions
    ######################################################################
    
    ######################################
    ##Pauli decomposition
    ######################################
    
    #why not just copy the previous one into new folder
#    destination=workstation+'\\'+GeoTiffOutputFolder+'\\'+InputDatafolder+'_D_pauli.tif'
#    if not os.path.isfile(destination):
#        source=workstation+'\\'+InputDatafolder+'\\'+PauliName      
#        shutil.copyfile(source, destination) 
    
    #Process The Function Soft/bin/bmp_process/create_pauli_rgb_file.exe
    #Arguments: 
    #-id "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01/T3" 
    #-of "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01/T3/PauliRGB.bmp" 
    #-iodf T3 -ofr 0 -ofc 0 -fnr 19563 -fnc 20848 -auto 1  
    #-errf "C:/Users/wayne/AppData/Local/Temp/PolSARpro-Bio_6.0.1/Tmp/MemoryAllocError.txt" 
    #-mask "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01_LEE_POC/T3/mask_valid_pixels.bin"
    
    #create_pauli_rgb_file.exe
    #
    #Parameters:
    # (string)       -id     input directory
    # (string)       -of     output RGB BMP file
    # (string)       -iodf   input-output data format
    # (int)          -ofr    Offset Row
    # (int)          -ofc    Offset Col
    # (int)          -fnr    Final Number of Row
    # (int)          -fnc    Final Number of Col
    # (int)          -auto   Automatic color enhancement (1 / 0)
    # if automatic = 0
    # (float)        -minb   blue channel : min value
    # (float)        -maxb   blue channel : max value
    # (float)        -minr   red channel : min value
    # (float)        -maxr   red channel : max value
    # (float)        -ming   green channel : min value
    # (float)        -maxg   green channel : max value
    #
    #Optional Parameters:
    # (string)       -mask   mask file (valid pixels)
    # (string)       -errf   memory error file
    # (noarg)        -help   displays this message
    # (noarg)        -data   displays the help concerning Data Format parameter
    #
    #try:
    #    ExcludeProgram=softDir+'bmp_process\\'+'create_pauli_rgb_file.exe'
    #    subprocess.call(ExcludeProgram + " -id \"" + Parameter_od_T3 + \
    #                                     "\" -of \"" + Parameter_Pauli_of + \
    #                                     "\" -iodf T3 -ofr 0 -ofc 0 -fnr "+\
    #                                     str(grd_rows)+" -fnc "+str(grd_cols)+\
    #                                     " -auto 1 -errf \""+ Parameter_errf+\
    #                                     "\" -mask \""+ Parameter_od_T3 +\
    #                                     "\\mask_valid_pixels.bin"+"\"")
    #except subprocess.CalledProcessError as e:
    #    raise RuntimeError("process_pauli command '{}' "+\
    #                       "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
    ######################################
    #H/A/Alpha decompositions
     ######################################
     
    #Process The Function Soft/bin/data_process_sngl/h_a_alpha_decomposition.exe
    #Arguments: 
    #-id "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01/T3" 
    #-od "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01/T3" 
    #-iodf T3 -nwr 1 -nwc 1 -ofr 0 -ofc 0 -fnr 19563 -fnc 20848 -fl1 0 -fl2 0 -fl3 1 -fl4 1 -fl5 1 -fl6 0 -fl7 0 -fl8 0 -fl9 0  
    #-errf "C:/Users/wayne/AppData/Local/Temp/PolSARpro-Bio_6.0.1/Tmp/MemoryAllocError.txt" 
    #-mask "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01/T3/mask_valid_pixels.bin"
    #h_a_alpha_decomposition.exe
    #
    #Parameters:
    # (string)       -id     input directory
    # (string)       -od     output directory
    # (string)       -iodf   input-output data format
    # (int)          -nwr    Nwin Row
    # (int)          -nwc    Nwin Col
    # (int)          -ofr    Offset Row
    # (int)          -ofc    Offset Col
    # (int)          -fnr    Final Number of Row
    # (int)          -fnc    Final Number of Col
    # (int)          -fl1    Flag Parameters (0/1)
    # (int)          -fl2    Flag Lambda (0/1)
    # (int)          -fl3    Flag Alpha (0/1)
    # (int)          -fl4    Flag Entropy (0/1)
    # (int)          -fl5    Flag Anisotropy (0/1)
    # (int)          -fl6    Flag Comb HA (0/1)
    # (int)          -fl7    Flag Comb H1mA (0/1)
    # (int)          -fl8    Flag Comb 1mHA (0/1)
    # (int)          -fl9    Flag Comb 1mH1mA (0/1)
    try:
        ExcludeProgram=softDir+'data_process_sngl\\'+'h_a_alpha_decomposition.exe'
        subprocess.call(ExcludeProgram + " -id \"" + Parameter_od_T3 + \
                                         "\" -od \"" + Parameter_H_A_Alpha_od + \
                                         "\" -iodf T3 -nwr 3 -nwc 3 -ofr 0 -ofc 0 -fnr "+\
                                         str(grd_rows)+" -fnc "+str(grd_cols)+\
                                         " -fl1 0 -fl2 1 -fl3 1 -fl4 1 -fl5 1 "+\
                                         "-fl6 0 -fl7 0 -fl8 0 -fl9 0 -errf \""+ Parameter_errf+\
                                         "\" -mask \""+ Parameter_od_T3 +\
                                         "\\mask_valid_pixels.bin"+"\"")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("process_H_A_Alpha  command '{}' "+\
                           "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
    
    ######################################
    #Freeman-Durden decompositions
    ######################################
    #
    #Process The Function Soft/bin/data_process_sngl/freeman_decomposition.exe
    #Arguments: 
    #-id "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01/T3" 
    #-od "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01/T3" 
    #-iodf T3 -nwr 1 -nwc 1 -ofr 0 -ofc 0 -fnr 19563 -fnc 20848  
    #-errf "C:/Users/wayne/AppData/Local/Temp/PolSARpro-Bio_6.0.1/Tmp/MemoryAllocError.txt" 
    #-mask "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01/T3/mask_valid_pixels.bin"
    #
    #Parameters:
    # (string)       -id     input directory
    # (string)       -od     output directory
    # (string)       -iodf   input-output data format
    # (int)          -nwr    Nwin Row
    # (int)          -nwc    Nwin Col
    # (int)          -ofr    Offset Row
    # (int)          -ofc    Offset Col
    # (int)          -fnr    Final Number of Row
    # (int)          -fnc    Final Number of Col
    #
    #Optional Parameters:
    # (string)       -mask   mask file (valid pixels)
    # (string)       -errf   memory error file
    # (noarg)        -help   displays this message
    # (noarg)        -data   displays the help concerning Data Format parameter    
    
    try:
        ExcludeProgram=softDir+'data_process_sngl\\'+'freeman_decomposition.exe'
        subprocess.call(ExcludeProgram + " -id \"" + Parameter_od_T3 + \
                                         "\" -od \"" + Parameter_Freeman_od + \
                                         "\" -iodf T3 -nwr 3 -nwc 3 -ofr 0 -ofc 0 -fnr "+\
                                         str(grd_rows)+" -fnc "+str(grd_cols)+\
                                         " -errf \""+ Parameter_errf+\
                                         "\" -mask \""+ Parameter_od_T3 +\
                                         "\\mask_valid_pixels.bin"+"\"")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("process_Freeman_Durden command '{}' "+\
                           "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        


    
    