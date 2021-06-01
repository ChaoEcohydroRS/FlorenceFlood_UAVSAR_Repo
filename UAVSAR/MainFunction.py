# -*- coding: utf-8 -*-

"""
Created on Wed Dec 11 13:40:22 2019

1) Extract polarimetric with Polsarpro (local)
2) Preprocessing POLSAR data, such as Speckle filter and POC (local)

3) Apply the radimetric decomposition to get the backscattering decomposition parameters (local)

4) Uploading appendix files to GEE and calculating the incidence angle for terrain correction (GEE)
(why not do it on GEE? because I will conduct the decomposition after correction.)

5) After applying radimetric terrain correction, (local)
uploading all 9 image files and calculating the factors for normalization (GEE)

6) Apply the radimetric normalization based on factors (local)

7) classification or segemetation?

8) Apply the water detection and flooding forested detection

9) Different method? RF or Deep Learning

@author: chao wang
waynechao128@gmail.com
"""

import os
import shutil
import glob
import time
#Execute a python script in a specific directory
mydir = 'C:\\Users\\wayne\\OneDrive\\Documents\\Tools\\PythonScript\\UAVSAR'#os.getcwd() # would be the MAIN folder
mydir_tmp = mydir + "\\PolarSARpro" # add the testA folder name
mydir_new = os.chdir(mydir_tmp) # change the current working directory
mydir = os.getcwd() # set the main directory again, now it calls testA
print(mydir)
import ExtractPolarimetricSAR_1
import ConvertHH_HV_VV2Geotiff_1
import PolarimetricDecomposition_1
import ConvertDecompositions2Geotiff_1
import RadiometricNormalization_7
import PolarimetricSegmentation_8

#Execute a python script in a specific directory
mydir = 'C:\\Users\\wayne\\OneDrive\\Documents\\Tools\\PythonScript\\UAVSAR'#os.getcwd() # would be the MAIN folder
mydir_tmp = mydir + "\\GEE_API_based" # add the testA folder name
mydir_new = os.chdir(mydir_tmp) # change the current working directory
mydir = os.getcwd() # set the main directory again, now it calls testA

import UploadGeoTiff2CloudStorage_2
import TransferGeotiff2GEE_3
import DownloadIncidenceAngle_4
import UpdateEarthEngineAssetsProperty_5
import GetNormalizationCorrectionParameters_6


def service_func():
    print('processing beginning')


######################################################################
###############Users input parameters ###############
#####################################################################

if __name__ == '__main__':
    
    
    #we sepearete the steps into 5 and give value of 1 or 2 or 3...8
    Step = 6
    
    #set google drive dir
    GoogleDriveDir='C:\\Users\\wayne\\Google Drive\\'
    
#    workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar_experiment'
#    workstation='D:\\Data\\UAVSAR'
    workstation='F:\\UAVSAR_NC'


#    ##input
#    InputDatafolder='UA_neuser_32023_18065_002_180918_L090_CX_01'
#    InputDatafolder='UA_neuser_32023_18067_000_180920_L090_CX_01'
#    InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
#    InputDatafolderList=['UA_neuser_32023_18068_000_180922_L090_CX_01']

#    InputDatafolder='UA_cpfear_13510_18065_008_180918_L090_CX_01'
#    InputDatafolder=['']         
#    InputDatafolder='UA_cpfear_13510_18069_005_180923_L090_CX_01'
    
    
#    InputDatafolderList=['UA_cpfear_35303_18069_004_180923_L090_CX_01',
#                         'UA_cpfear_35303_18067_002_180920_L090_CX_01',
#                         'UA_cpfear_35303_18065_004_180918_L090_CX_01',
#                         'UA_lumber_31509_18069_006_180923_L090_CX_01',
#                         'UA_lumber_31509_18065_009_180918_L090_CX_01']


#'UA_neuser_32023_18065_002_180918_L090_CX_01',
#                         'UA_neuser_32023_18067_000_180920_L090_CX_01',
#                         'UA_neuser_32023_18068_000_180922_L090_CX_01',
#                         'UA_neuser_32023_18069_002_180923_L090_CX_01'                         


#    InputDatafolderList=[
##            'UA_cpfear_13510_18065_008_180918_L090_CX_01',
##            'UA_cpfear_13510_18069_005_180923_L090_CX_01',
##            'UA_cpfear_13510_18067_003_180920_L090_CX_01',
##            'UA_cpfear_13510_18066_005_180919_L090_CX_01'
#            'UA_cpfear_13510_18068_003_180922_L090_CX_01',
#            
##            'UA_cpfear_35303_18065_004_180918_L090_CX_01',
##            'UA_cpfear_35303_18067_002_180920_L090_CX_01',
##            'UA_cpfear_35303_18066_002_180919_L090_CX_01',
##            'UA_cpfear_35303_18068_002_180922_L090_CX_01',
##            'UA_cpfear_35303_18069_004_180923_L090_CX_01',
#             
##            'UA_lumber_31509_18066_006_180919_L090_CX_01',
##            'UA_lumber_31509_18067_004_180920_L090_CX_01',
##            'UA_lumber_31509_18069_006_180923_L090_CX_01',
##            'UA_lumber_31509_18065_009_180918_L090_CX_01',
##            'UA_lumber_31509_18068_004_180922_L090_CX_01'
#            ]


    InputDatafolderList=[
#            'UA_cpfear_13510_18065_008_180918_L090_CX_01',
#            'UA_cpfear_13510_18069_005_180923_L090_CX_01',
#            'UA_cpfear_13510_18067_003_180920_L090_CX_01',
#            'UA_cpfear_13510_18066_005_180919_L090_CX_01'
            'UA_padelE_36000_19059_003_190904_L090_CX_01',
            ]

#                     

#    InputDatafolderList=[
#                         'UA_cpfear_35303_18069_004_180923_L090_CX_01',
##                         'UA_cpfear_35303_18067_002_180920_L090_CX_01',
#                         'UA_cpfear_35303_18065_004_180918_L090_CX_01',
#                         'UA_lumber_31509_18069_006_180923_L090_CX_01',
#                         'UA_lumber_31509_18065_009_180918_L090_CX_01']
   
#    InputDatafolderList=['UA_cpfear_13510_18065_008_180918_L090_CX_01',
#                         'UA_cpfear_13510_18069_005_180923_L090_CX_01']
    
    
#    InputDatafolderList=['UA_peedee_15100_18064_002_180917_L090_CX_01',
#                         'UA_peedee_15100_18069_007_180923_L090_CX_01']
    
    #loop the daily SAR observation
    for InputDatafolder in InputDatafolderList:

        os.chdir(workstation + '\\' + InputDatafolder)
#        for Paulifile in glob.glob("*pauli.tif"): 
#            PauliName=Paulifile
#            print(PauliName)
            
        GeoTiffOutputFolder=InputDatafolder[0:InputDatafolder.find('_00')+1] +'Cols'
        OutputDataFolder=InputDatafolder[0:InputDatafolder.find('_00')+1] + 'Processing'
        
        if not os.path.exists(workstation + '\\' + GeoTiffOutputFolder):
            os.makedirs(workstation + '\\' + GeoTiffOutputFolder)
        
        if not os.path.exists(workstation + '\\' + OutputDataFolder):
            os.makedirs(workstation + '\\' + OutputDataFolder)
    
        # service.py executed as script
        # do something
        service_func()
        
        #beginning
        if Step == 1: 
            #begin to extract T3 matrix and do some speckle filter
            #and convert the inc into geotiff
            ExtractPolarimetricSAR_1._func(workstation,InputDatafolder,
                                           GeoTiffOutputFolder,OutputDataFolder)
#            
#            #begin to extract T3 matrix and do some speckle filter
#            #and convert the inc into geotiff
#            ConvertHH_HV_VV2Geotiff_1._func(workstation,InputDatafolder,
#                                           GeoTiffOutputFolder,OutputDataFolder)
#            
            #begin to extract decomposition
            PolarimetricDecomposition_1._func(workstation,InputDatafolder,\
                                           GeoTiffOutputFolder,OutputDataFolder)
            
            #convert the decomposition into geotiff
            ConvertDecompositions2Geotiff_1._func(workstation,InputDatafolder,
                                           GeoTiffOutputFolder,OutputDataFolder)
            
        elif Step == 2:
            #upload the decompositions and other parameters(HHHH, VVVV, HVHV)
            #turn to the google cloud storage  5
            UploadGeoTiff2CloudStorage_2._func(workstation,InputDatafolder,
                                           GeoTiffOutputFolder,OutputDataFolder)
            
                    
        elif Step == 3:
            #transfer geotiff from CS to EE
            TransferGeotiff2GEE_3._func(workstation,InputDatafolder,
                                           GeoTiffOutputFolder,OutputDataFolder)
            
            
        elif Step == 4:
            #get the Incidence angle
            DownloadIncidenceAngle_4._func(workstation,InputDatafolder,
                                           GeoTiffOutputFolder,OutputDataFolder)
            
        
        elif Step == 5:
            #transfer IA from drive to workspace
            #os.rename("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
            #shutil.move("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
            #os.replace（"path/to/current/file.foo", "path/to/new/destination/for/file.foo")
            #'C:\\Users\\wayne\\Google Drive\\SolarPV\\'+GeoTiffOutputFolder+'RadNormFactors.csv'
            
            #copy the incidence angle
            source=GoogleDriveDir+InputDatafolder+'_IA.tif'
            destination=workstation + '\\' + GeoTiffOutputFolder + \
            '\\' + InputDatafolder + '_IA.tif'
            
            #check if the IA exists, if not copy it from Google Drive
            if os.path.isfile(source):
#            if os.path.isfile(destination):
                if not os.path.isfile(destination):
                    dest = shutil.move(source, destination)
                    UpdateEarthEngineAssetsProperty_5._func(workstation,InputDatafolder,
                                               GeoTiffOutputFolder,OutputDataFolder)
                else:
                    UpdateEarthEngineAssetsProperty_5._func(workstation,InputDatafolder,
                                               GeoTiffOutputFolder,OutputDataFolder)
            else: print('IA file doesn"t exists! please wait for a while!!!')
            
            
        elif Step == 6:
            GetNormalizationCorrectionParameters_6._func(workstation,InputDatafolder,
                                           GeoTiffOutputFolder,OutputDataFolder)
            
            
        elif Step == 7:
            #path to the RadiometricNormalization factors
            RadNormFactorsCSVFile='C:\\Users\\wayne\\Google Drive\\SolarPV\\'+ \
            GeoTiffOutputFolder+'RadNormFactors.csv'
            #check if the IA exists, if not copy it from Google Drive
            if os.path.isfile(RadNormFactorsCSVFile):
                #the IA data should be masked with the other image
                #MaskIA_Geotiff
                
                #apply normalization function
                RadiometricNormalization_7._func(workstation,InputDatafolder,
                                           GeoTiffOutputFolder,OutputDataFolder)
            else: print('RadNormFactorsCSVFile doesn"t exists! please wait for a while!!!')
            
            
        elif Step == 8:
            PolarimetricSegmentation_8._func(workstation,InputDatafolder,
                                           GeoTiffOutputFolder,OutputDataFolder)
        
        
        #wait 30mins between each flightline to let SSD cool down
#        time.sleep(100)
#        time.sleep(1800)
            
            
        
    
    
    
