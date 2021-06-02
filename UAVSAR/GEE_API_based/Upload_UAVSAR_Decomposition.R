
library(intervals)
library(raster)
library(sp)
library('lidR')
library('rlas')
library(utils)
library(R.utils)

###############Above unzip the lidar CHM file######################

#set the workspace
workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\'
workstation='D:\\Data\\'


UAVSAR_Data_folder='uavsar_experiment'
UAVSAR_Data_folder='UAVSAR'





GeoTiffSUbFolder='UA_neuser_32023_18065_Cols'
# GeoTiffSUbFolder='UA_neuser_32023_18066_Cols'
# GeoTiffSUbFolder='UA_neuser_32023_18067_Cols'
# GeoTiffSUbFolder='UA_neuser_32023_18068_Cols'
# GeoTiffSUbFolder='UA_neuser_32023_18069_Cols'

#search unzipped folder and get the geotiff files list to be uploaded
#get the tiff file list
# GeoTiffFileNames=list('PR_5March2017_coastal3a_CHM','PR_7March2017_coastal3a_CHM')
GeoTiffFileNames=list.files(path=paste(workstation,UAVSAR_Data_folder,
                                       '\\',GeoTiffSUbFolder,
                                       '\\',sep=''),
                            pattern = '*.tif',recursive =FALSE)


GeoTiffFileNames

keyword='01_D'
RemoveGeoTiffFileNames=GeoTiffFileNames
for (fileName in RemoveGeoTiffFileNames){
  
  if (grepl(keyword, fileName)){
    print(fileName)
    #RemoveGeoTiffFileNames<- GeoTiffFileNames[!GeoTiffFileNames %in% fileName]
    RemoveGeoTiffFileNames<- RemoveGeoTiffFileNames[RemoveGeoTiffFileNames!=(fileName)]
  }
  
}


GeoTiffFileNames<- GeoTiffFileNames[!GeoTiffFileNames %in% RemoveGeoTiffFileNames]



#
#revised at Oct 10, 2019
#make it suitable for the project canopy height by lidar

# #create a collection for storage the dataset 
# cat(paste("earthengine --no-use_cloud_api create collection ",
#           "projects/GlobalReservoirs/UAVSAR/",GeoTiffSUbFolder,sep = ""),
#     "\n", file=paste(workstation,UAVSAR_Data_folder,'\\',GeoTiffSUbFolder,
#                      '\\',"Upload_",GeoTiffSUbFolder,"_GSC2Asset.bat",sep=""),
#     sep = " ",append = FALSE)
# 
# # #just in case the script running too fast the system cannot respond
# # #so just wait 10 seconds when each upload task submitted
# cat("timeout 10 >nul", "\n",
#     file=paste(workstation,UAVSAR_Data_folder,'\\',GeoTiffSUbFolder,
#                '\\',"Upload_",GeoTiffSUbFolder,"_GSC2Asset.bat",sep=""),
#     sep = " ",append = TRUE)

#
#create commond to transfer each tif file from google cloud storage to the Google Earth Engine asset using the earth engine commomd
#
List<-c()
OrderList<-c()
for (TifFileName in GeoTiffFileNames){
  #TifFileName=TifFileNames[1]

  #get the base name
  baseName<-sub(pattern = "(.*)\\..*$", 
                replacement = "\\1", 
                basename(TifFileName))
  
  ##UA_neuser_32023_18065_002_180918_L090_CX_01_hgt
  ##UA_neuser_32023_18065_002_180918_L090_CX_01_T11
  #IS _T exist, if not, just last 3, otherwise, from _T to End
  if(grepl('_T', baseName)){
    FindIndex<-gregexpr(pattern ='_T',baseName)
    propertyName<-substr(baseName, FindIndex[[1]]+1, nchar(baseName))
  }else{
    propertyName<-substr(baseName, nchar(baseName)-3+1, nchar(baseName))
  }
  
  # 
  # 
  # prepare the earth engine commond for transfer data
  cat(paste("earthengine --no-use_cloud_api upload image ",
            "--asset_id=projects/GlobalReservoirs/UAVSAR/",GeoTiffSUbFolder,"/",
            baseName," --pyramiding_policy=sample gs://aviris_ng/",
            baseName,".tif",sep = ""), "\n",
      file=paste(workstation,UAVSAR_Data_folder,'\\',GeoTiffSUbFolder,
                 '\\',"Upload_Decomposite",GeoTiffSUbFolder,"_GSC2Asset.bat",sep=""),
      sep = " ",append = TRUE)
  
  # #just in case the script running too fast the system cannot respond
  # #so just wait 10 seconds when each upload task submitted
  cat("timeout 10 >nul", "\n",
      file=paste(workstation,UAVSAR_Data_folder,'\\',GeoTiffSUbFolder,
                 '\\',"Upload_Decomposite",GeoTiffSUbFolder,"_GSC2Asset.bat",sep=""),
      sep = " ",append = TRUE)
  
  #it is not a good idea set the property when uploading image
  # ###set the property name
  # ###earthengine asset set -p '(string)name=42' users/username/asset_id
  # cat(paste("earthengine --no-use_cloud_api asset set -p ",
  #           '"(string)name=',propertyName,'" ',
  #           "projects/GlobalReservoirs/UAVSAR/",GeoTiffSUbFolder,"/",
  #           baseName,sep = ""), "\n",
  #     file=paste(workstation,UAVSAR_Data_folder,'\\',GeoTiffSUbFolder,
  #                '\\',"Upload_",GeoTiffSUbFolder,"_GSC2Asset.bat",sep=""),
  #     sep = " ",append = TRUE)
  
}
