# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 11:37:49 2020

@author: wayne
"""

import glob
import shutil
from google.cloud import storage
import os
#import multiprocessing

#function used for uploading
def upload_blob(source_file_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"
    
    #set the target filename saving in the cloud
    #os.path.splitext(os.path.basename(source_file_name))[0]
    destination_blob_name=os.path.basename(source_file_name)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucketName)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )
    return 1



#operating function
def _func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder):
    #delete the intermediate files which will not be used
    #to release the storage space
    ## Try to remove tree; if failed show an error using try...except on screen
    try:
        T3Folder=workstation+"/"+OutputDataFolder+"/T3"
        
        
        shutil.rmtree(T3Folder)
        
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
        
    try:
        
        SpeckleFilterT3Folder=workstation+"/"+OutputDataFolder+"/SpeckleFilter"
        
        shutil.rmtree(SpeckleFilterT3Folder)
        
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
        
    
    #set the parameters
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= \
    "C:\\Users\\wayne\\OneDrive\\Documents\\Tools\\PythonScript\\UAVSAR\\Proj2019-e44da331084f.json" 
    global bucketName
    bucketName="aviris_ng"
    
    #set the path to the data needs to upload
    rasterGeotiff_List=[]
    
    rasterGeotiff_Dir=workstation + "\\" + GeoTiffOutputFolder
    
    #get all elements of the tif matrix as a list to be applied
    os.chdir(rasterGeotiff_Dir)
    for geotiffFile in glob.glob("*.tif"):
        fullFilePath=workstation + '\\' + GeoTiffOutputFolder + '\\' + geotiffFile
        rasterGeotiff_List.append(fullFilePath)
        
    
#    # upload the raster using map()
#    print(rasterGeotiff_List)
#    pool = multiprocessing.Pool(4)
#    result = zip(*pool.map(upload_blob, rasterGeotiff_List))
#    #result = map(upload_blob, rasterGeotiff_List) 
#    print(result)

    
    #begin to conduct the operation on each T3 maxtrix element
    for rasterName in rasterGeotiff_List:
        print(rasterName)
        
        #get the source file path waiting for uploading
        sourceFileName= rasterName
   
        #set the file waiting for uploading
        upload_blob(sourceFileName)





