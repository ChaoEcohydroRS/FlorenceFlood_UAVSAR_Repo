# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 23:43:28 2020

@author: wayne
"""
import os
import time
import subprocess
import glob
import shutil



#operating function
##############################################################################

def _func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder):

    #create a collection for storage the dataset
    try:
        ExcludeProgram='earthengine create collection '+ \
        'projects/GlobalReservoirs/UAVSAR/' + GeoTiffOutputFolder
        #print(ExcludeProgram)
        
        subprocess.call(ExcludeProgram)
        #just in case the script running too fast the system cannot respond
        #so just wait 10 seconds when each upload task submitted
        time.sleep(5)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("earthengine asset name  command '{}' "+\
                           "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
    
    #transfer each geotiff from GCS to GEE asset 
    #using the earth engine commomd
    rasterGeotiff_List=[]
    rasterGeotiff_Dir=workstation + '\\' + GeoTiffOutputFolder
    #get all elements of the tif matrix as a list to be applied
    os.chdir(rasterGeotiff_Dir)
    
    ##get all geotiff file as a list to be applied
    for geotiffFile in glob.glob("*.tif"):
#    for geotiffFile in glob.glob("*P*.tif"):
        fullFilePath=geotiffFile
        rasterGeotiff_List.append(fullFilePath)
        
    ##filter pauli decomposition var
    #DecompositeGeotiff_List_Filtered=[element for element in DecompositeGeotiff_List if 'D_pauli' not in element]
    
    #begin to conduct the operation on each T3 maxtrix element
    for rasterFileName in rasterGeotiff_List:
        baseName=os.path.splitext(os.path.basename(rasterFileName))[0]
        try:
            ExcludeProgram='earthengine upload image '+ \
            '--asset_id=projects/GlobalReservoirs/UAVSAR/'+\
            GeoTiffOutputFolder+'/'+baseName+\
            ' --pyramiding_policy=mean gs://aviris_ng/'+\
            baseName+'.tif'
            #print(ExcludeProgram)
            
            subprocess.call(ExcludeProgram)
            time.sleep(5)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("earthengine asset name  command '{}' "+\
                               "return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


#workstation='D:\\Data\\UAVSAR'
#InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18069_Cols'
#OutputDataFolder='UA_neuser_32023_18069_Processing'
#
#PauliName='neuser_32023_18065_002_180918_L090_CX_01_pauli.tif'
#InputDatafolder='UA_neuser_32023_18065_002_180918_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18065_Cols'
#OutputDataFolder='UA_neuser_32023_18065_Processing'

#_func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder)



    
    