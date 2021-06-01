# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 21:43:43 2019
this module used to call polsarpro to extract polarimetric sar data
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
from ConvertHDR2Geotiff import load_ENVI_data
from ConvertHDR2Geotiff import load_BMP_data
from ConvertHDR2Geotiff import array2raster


def _func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder):

    
    ######################################################################
    ###############Using PolSARPRO extract data###############
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
    Parameter_od_T3=workstation+"\\"+OutputDataFolder+"\\T3"
    Parameter_speckle_filter_od_T3=workstation+"\\"+OutputDataFolder+"\\SpeckleFilter\\T3"
#    Parameter_POC_od_T3=workstation+"\\"+OutputDataFolder+"\\POC\\T3"
    
    if not os.path.exists(Parameter_od_T3):
        os.makedirs(Parameter_od_T3)
        
    if not os.path.exists(Parameter_speckle_filter_od_T3):
        os.makedirs(Parameter_speckle_filter_od_T3)
        
#    if not os.path.exists(Parameter_POC_od_T3):
#        os.makedirs(Parameter_POC_od_T3)
    
    Parameter_errf="C:/Users/wayne/AppData/Local/Temp/PolSARpro-Bio_6.0.1/Tmp/MemoryAllocError.txt"
    Parameter_Configf="C:/Users/wayne/AppData/Local/Temp/PolSARpro-Bio_6.0.1/Tmp/2019_11_02_21_46_42_uavsar_config.txt"
    
    #uavsar_header
    #-id input directory
    #-od output directory
    #-fnr final number of row
    #-fnc final number of col
    #-hf input annotation file
    
    try:
        ExcludeProgram=softDir+'data_import\\'+'uavsar_header.exe'
        subprocess.call(ExcludeProgram + " -hf \"" + Parameter_hf + \
                                         "\" -id \"" + Parameter_id + \
                                         "\" -od \"" + Parameter_od + \
                                         "\" -df grd -tf \""+Parameter_Configf+"\"")
    
    except subprocess.CalledProcessError as e:
        raise RuntimeError("uavsar_header command '{}' "+\
                           "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
    Parameter_if1=grdFiles_List[0]
    Parameter_if2=grdFiles_List[1]
    Parameter_if3=grdFiles_List[2]
    Parameter_if4=grdFiles_List[3]
    Parameter_if5=grdFiles_List[4]
    Parameter_if6=grdFiles_List[5]
    
    #uavsar_convert_MLC
    #-hf input annotation file
    #-mem Allocated memory for blocksize determination(in Mb)
    try:
        ExcludeProgram=softDir+'data_import\\'+'uavsar_convert_MLC.exe'
        subprocess.call(ExcludeProgram + " -hf \"" + Parameter_hf + \
                                         "\" -if1 \"" + Parameter_if1 + \
                                         "\" -if2 \"" + Parameter_if2 + \
                                         "\" -if3 \"" + Parameter_if3 + \
                                         "\" -if4 \"" + Parameter_if4 + \
                                         "\" -if5 \"" + Parameter_if5 + \
                                         "\" -if6 \"" + Parameter_if6 + \
                                         "\" -od \"" + Parameter_od_T3 + \
                                         "\" -odf T3 -inr "+str(grd_rows)+" -inc "+str(grd_cols)+\
                                         " -ofr 0 -ofc 0 -fnr "+str(grd_rows)+" -fnc "+str(grd_cols)+\
                                         "  -nlr 1 -nlc 1 -ssr 1 -ssc 1 -mem 4000 -errf \""+ Parameter_errf+"\"")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("uavsar_convert_MLC command '{}' "+\
                           "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
    
    #create_mask_valid_pixels
    try:
        ExcludeProgram=softDir+'tools\\'+'create_mask_valid_pixels.exe'
        subprocess.call(ExcludeProgram + " -id \"" + Parameter_od_T3 + \
                                         "\" -od \"" + Parameter_od_T3 + \
                                         "\" -idf T3 -ofr 0 -ofc 0 -fnr "+str(grd_rows)+" -fnc "+str(grd_cols))
    except subprocess.CalledProcessError as e:
        raise RuntimeError("create_mask_valid_pixels command '{}' "+\
                           "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
    
    # Copy the content of 
    # source to destination 
    #copy the config.txt for the speckle_filter processing
    source=Parameter_od_T3+'\\config.txt'
    destination=Parameter_speckle_filter_od_T3+'\\config.txt'
    if not os.path.isfile(destination):
        shutil.copyfile(source, destination) 
    
    
    
    #speckle_filter: lee_refined_filter with 3*3 pixels
    #Process The Function Soft/bin/speckle_filter/lee_refined_filter.exe
    #Arguments: -id "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/"+
    #"UA_neuser_32023_18065_002_180918_L090_CX_01/T3" -od 
    #"C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01_LEE/T3" 
    #-iodf T3 -nw 3 -nlk 13 -ofr 0 -ofc 0 -fnr 19563 -fnc 20848  -errf 
    #"C:/Users/wayne/AppData/Local/Temp/PolSARpro-Bio_6.0.1/Tmp/MemoryAllocError.txt" 
    #-mask "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01/T3/mask_valid_pixels.bin"
    try:
        ExcludeProgram=softDir+'speckle_filter\\'+'lee_refined_filter.exe'
        subprocess.call(ExcludeProgram + " -id \"" + Parameter_od_T3 + \
                                         "\" -od \"" + Parameter_speckle_filter_od_T3 + \
                                         "\" -iodf T3 -nw 3 -nlk 13 -ofr 0 -ofc 0 -fnr "+\
                                         str(grd_rows)+" -fnc "+str(grd_cols)+\
                                         " -errf \""+ Parameter_errf+\
                                         "\" -mask \""+ Parameter_od_T3 + "\\mask_valid_pixels.bin"+"\"")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("lee_refined_filter command '{}' "+\
                           "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
    
    #create_mask_valid_pixels in a new folder
    #why not just copy the previous one into new folder
    #############
    source=Parameter_od_T3+'\\mask_valid_pixels.bin'
    destination=Parameter_speckle_filter_od_T3+'\\mask_valid_pixels.bin'
    if not os.path.isfile(destination):
        shutil.copyfile(source, destination) 

##unnecessary to conduc mask create
#    try:
#        ExcludeProgram=softDir+'tools\\'+'create_mask_valid_pixels.exe'
#        subprocess.call(ExcludeProgram + " -id \"" + Parameter_od_T3 + \
#                                         "\" -od \"" + Parameter_speckle_filter_od_T3 + \
#                                         "\" -idf T3 -ofr 0 -ofc 0 -fnr "+str(grd_rows)+" -fnc "+str(grd_cols))
#    except subprocess.CalledProcessError as e:
#        raise RuntimeError("create_mask_valid_pixels command '{}' "+\
#                           "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
    
    
    #set the folder to write the hdr files
    Parameter_od_T3=Parameter_speckle_filter_od_T3
    T3Folder=Parameter_od_T3+'\\'#workstation+subfolder+'T3\\'
    annfolder=Parameter_id+'\\'#workstation+subfolder
    
    #create the T3 matrix hdr
    create_bin_header(T3Folder,annfolder)
    
#    #create_mask_valid_pixels in a new folder
#    #why not just copy the previous one into new folder
#    #############
#    source=Parameter_speckle_filter_od_T3+'\\mask_valid_pixels.bin'
#    destination=Parameter_POC_od_T3+'\\mask_valid_pixels.bin'
#    if not os.path.isfile(destination):
#        shutil.copyfile(source, destination) 
#    
#    #copy the config.txt for the POC processing
#    sourceconfig=Parameter_speckle_filter_od_T3+'\\config.txt'
#    destinationconfig=Parameter_POC_od_T3+'\\config.txt'
#    if not os.path.isfile(destinationconfig):
#        shutil.copyfile(sourceconfig, destinationconfig) 
    
    #POC
    #Process The Function Soft/bin/data_process_sngl/orientation_estimation.exe
    #Arguments: 
    #-id "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01_LEE/T3" 
    #-od "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01_LEE_POC/T3" 
    #-iodf T3 -nwr 1 -nwc 1 -ofr 0 -ofc 0 -fnr 19563 -fnc 20848  
    #-errf "C:/Users/wayne/AppData/Local/Temp/PolSARpro-Bio_6.0.1/Tmp/MemoryAllocError.txt" 
    #-mask "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01_LEE/T3/mask_valid_pixels.bin"
    #
#    try:
#        ExcludeProgram=softDir+'data_process_sngl\\'+'orientation_estimation.exe'
#        subprocess.call(ExcludeProgram + " -id \"" + Parameter_speckle_filter_od_T3 + \
#                                         "\" -od \"" + Parameter_POC_od_T3 + \
#                                         "\" -iodf T3 -nwr 1 -nwc 1 -ofr 0 -ofc 0 -fnr "+\
#                                         str(grd_rows)+" -fnc "+str(grd_cols)+\
#                                         " -errf \""+ Parameter_errf+\
#                                         "\" -mask \""+ Parameter_POC_od_T3 + "\\mask_valid_pixels.bin"+"\"")
#    except subprocess.CalledProcessError as e:
#        raise RuntimeError("lee_refined_filter command '{}' "+\
#                           "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
    #Process The Function Soft/bin/data_process_sngl/orientation_correction.exe
    #Arguments: 
    #-id "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01_LEE/T3" 
    #-od "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01_LEE_POC/T3" 
    #-if "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01_LEE_POC/T3/orientation_estimation.bin" 
    #-iodf T3 -ofr 0 -ofc 0 -fnr 19563 -fnc 20848  
    #-errf "C:/Users/wayne/AppData/Local/Temp/PolSARpro-Bio_6.0.1/Tmp/MemoryAllocError.txt" 
    #-mask "C:/Workstation/NC_Study/UAVSAR/Data/uavsar_experiment/UA_neuser_32023_18065_002_180918_L090_CX_01_LEE/T3/mask_valid_pixels.bin"
    #
#    try:
#        Parameter_if_orientation=Parameter_POC_od_T3+"\\"+"orientation_estimation.bin"
#        ExcludeProgram=softDir+'data_process_sngl\\'+'orientation_correction.exe'
#        subprocess.call(ExcludeProgram + " -id \"" + Parameter_speckle_filter_od_T3 + \
#                                         "\" -od \"" + Parameter_POC_od_T3 + \
#                                         "\" -if \"" + Parameter_if_orientation + \
#                                         "\" -iodf T3 -ofr 0 -ofc 0 -fnr "+\
#                                         str(grd_rows)+" -fnc "+str(grd_cols)+\
#                                         " -errf \""+ Parameter_errf+\
#                                         "\" -mask \""+ Parameter_POC_od_T3 + "\\mask_valid_pixels.bin"+"\"")
#    except subprocess.CalledProcessError as e:
#        raise RuntimeError("orientation_correction command '{}' "+\
#                           "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

    
#    #Set the parameters for the further processing
#    Parameter_od_T3=Parameter_POC_od_T3
#    T3Folder=Parameter_od_T3+'\\'#workstation+subfolder+'T3\\'
#    annfolder=Parameter_id+'\\'#workstation+subfolder
#    
#    #create the T3 matrix hdr
#    create_bin_header(T3Folder,annfolder)
    
    
    ######################################################################
    ########Convert to geotiff (hgt, inc, and mask files) ###########
    #####################################################################
    
    ## Open mask file and convert it to tiff
    #mask_file_name=workstation+subfolder+\
    #"T3\\mask_valid_pixels.bin"
    
    mask_file_name=Parameter_od_T3+\
    "\\mask_valid_pixels.bin"
    data, geodata = load_ENVI_data(mask_file_name)
    
    # Write it out as a geotiff
    geotiff_mask_out=Parameter_od_T3+\
    "\\mask_valid_pixels.tif"
    #export mask file to tif format
    array2raster(data, geodata, geotiff_mask_out, gdal_driver='GTiff')
    
    #copy to the cols folder for uploading
    source=geotiff_mask_out
    destination=workstation+'\\'+GeoTiffOutputFolder+'\\'+\
    InputDatafolder+"_M_mask.tif"
    if not os.path.isfile(destination):
        shutil.copyfile(source, destination) 
        
 

#    #height 
#    Parameter_if_hgt=workstation+"/"+InputDatafolder+"/"+hgtFile
       
#    #uavsar_convert_dem
#    try:
#        ExcludeProgram=softDir+'data_import\\'+'uavsar_convert_dem.exe'
#        subprocess.call(ExcludeProgram + " -hf \"" + Parameter_hf + \
#                                         "\" -if \"" + Parameter_if_hgt + \
#                                         "\" -od \"" + Parameter_od_T3 + \
#                                         "\" -inr "+str(grd_rows)+" -inc "+str(grd_cols)+\
#                                         " -ofr 0 -ofc 0 -fnr "+str(grd_rows)+" -fnc "+str(grd_cols)+""+\
#                                         "  -nlr 1 -nlc 1 -ssr 1 -ssc 1 -mem 3000 -errf \""+ Parameter_errf+"\"")
#    except subprocess.CalledProcessError as e:
#        raise RuntimeError("uavsar_convert_dem command '{}' "+\
#                           "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


      
#    ######################################## 
#    #Open hgt and convert it to tif
#    hgt_file_name=Parameter_if_hgt
#    #read the data
#    data, geodata = load_ENVI_data(hgt_file_name)
    
#    # Write it out as a geotiff
#    hgt_filenameNoExt=os.path.splitext(os.path.basename(hgt_file_name))[0]
#    hgt_file_out=workstation+'\\'+GeoTiffOutputFolder+'\\UA_'+hgt_filenameNoExt+\
#    "_hgt.tif"
#    #convert hgt from bin format to tif format
#    array2raster(data, geodata, hgt_file_out, gdal_driver='GTiff') 
    
    ### Open inc and convert it to tif
    #inc_file_name=Parameter_id+'\\'+\
    #"neuser_32023_18067_000_180920_L090_CX_01.inc"
    
#    inc_file_name=Parameter_id+'\\'+IncFiles
#    data, geodata = load_ENVI_data(inc_file_name)
#    
#    # Write it out as a geotiff
#    inc_file_out=workstation+'\\'+GeoTiffOutputFolder+'\\UA_'+\
#    os.path.splitext(os.path.basename(IncFiles))[0]+"_inc.tif"
#    array2raster(data, geodata, inc_file_out, gdal_driver='GTiff')

#
###############################
###convert the polarimetric variable to geotiff format
##the list to be applied
##PolarimetricList=['T22','T33','T12_real',\
##                 'T13_imag','T13_real','T23_imag','T23_real']
#
##get all input
#T3_Matrix_Dir=Parameter_od_T3
#T3_Matrix_List=[]
##get all elements of the T3 matrix
#os.chdir(T3_Matrix_Dir)
#for file in glob.glob("T*.bin"):
#    T3_Matrix_List.append(file)
#
#
#for T3CMRasterName in T3_Matrix_List:  
#    ## Open some data inc /neuser_32023_18067_000_180920_L090_CX_01.hgt
#    file_name=Parameter_od_T3+'\\'+T3CMRasterName
#    data, geodata = load_data(file_name)
#    
#    # Write it out as a geotiff
#    dataVar=os.path.splitext(os.path.basename(T3CMRasterName))[0]
#    file_out=workstation+'\\'+GeoTiffOutputFolder+'\\UA_'+\
#    os.path.splitext(os.path.basename(IncFiles))[0]+"_"+dataVar+".tif"
#    array2raster(data, geodata, file_out, gdal_driver='GTiff') 
















