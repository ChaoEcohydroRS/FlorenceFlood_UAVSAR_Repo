"""
######################################################################################################### 
##                                                                                                    #\\
##             UAVSAR Incidence angle get and download                  #\\
##                                                                                                    #\\
#########################################################################################################
# date: 2019-12-01
# author:  Chao Wang | chao.wang@unc.edu | waynechao128@gmail.com
# Postdoc at the university of North Carolina-Chapel Hill
# supported by Dr. Tamlin M. Pavelsky for the projects of DEEPP and ABoVE
##--------------------------------------------------------
transfer from the javascript code
#https://code.earthengine.google.com/9fcb622572910bbee371ea3d810ea7b6
"""

import sys
import ee
import math
import re
import os



######################################################################################################### 
##                                                                                                    #\\
##              Functions defination                  #\\
##                                                                                                    #\\
#########################################################################################################

#define function to calculate the coordinate difference
def coord_dif(geom1, geom2, ind):
    return ee.Number(geom1.coordinates().get(ind)
                     ).subtract(ee.Number(geom2.coordinates().get(ind)))

#define a function to move a line to a distance
def move(geom, x, y):
    #move geometry xs and ys to certain x and y
    xs = ee.Array(geom.coordinates()).slice(1,0,1).add(x)
    ys = ee.Array(geom.coordinates()).slice(1,1,2).add(y)
    #get the new coords array list
    new_coords = ee.Array.cat([xs,ys], 1)
    #return the moved line
    return ee.Feature(ee.Geometry.LineString(new_coords.toList()))

#define conversion functions to convert from/to dB
def toNatural(img):return ee.Image(10.0).pow(img.divide(10.0))
def toDB(img):return ee.Image(img).log10().multiply(10.0)


#for scienfic notion, check if it is a number
def is_number_tryexcept(s):
    """ Returns True is string is a number. """
    try:
        float(s)
        return True
    except ValueError:
        return False

###-----------End Functions defination-------------------------------



######################################################################################################### 
##                                                                                                    #\\
##              User Input Parameters                  #\\
##                                                                                                    #\\
#########################################################################################################

#workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar_experiment'
#workstation='D:\\Data\\UAVSAR'


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



####-----------End User Input Parameters-------------------------------------



##############################################################################\\
##
##             Read information from annotation begin                 #\\
##                                                                           
########################################################################\\
#global LC2016
#global LandTypeValue

def _func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder): 
    
    #initialize the earthengine api
    ee.Initialize()
#    #get land cover dataset
#    NLCD2016 = ee.Image("USGS/NLCD/NLCD2016")
#    LC2016=NLCD2016.select('landcover')
#    
#    #41,42,43 forest
#    #82 crop
#    #11 water
#    LandTypeValue=11#82#41#42#43#7,8,9

    
    # Empty lists to put information that will be recalled later.
    grdFiles_List=[]
    Lines_list = []
    Samples_list = []
    Latitude_list = []
    Longitude_list = []
    Files_list = []
    PegLatitude_list=[]
    PegLongitude_list=[]
    PegHeading_list=[]
    AverageTerrainHeight_list=[]
    AverageAltitude_list=[]
    LookDirection_list=[]
    
    
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
                
        elif "Peg Latitude" in line:
            PegLatitude = [float(x) for x in line.split() if is_number_tryexcept(x)][0]
            if PegLatitude not in PegLatitude_list:
                PegLatitude_list.append(PegLatitude)
                
        elif "Peg Longitude" in line:
            PegLongitude = [float(x) for x in line.split() if is_number_tryexcept(x)][0]
            if PegLongitude not in PegLongitude_list:
                PegLongitude_list.append(PegLongitude)
                
        elif "Peg Heading" in line:
            PegHeading = [float(x) for x in line.split() if is_number_tryexcept(x)][0]
            if PegHeading not in PegHeading_list:
                PegHeading_list.append(PegHeading)
                
        elif "Global Average Terrain Height" in line:
            AverageTerrainHeight = [float(x) for x in line.split() if is_number_tryexcept(x)][0]
            if AverageTerrainHeight not in AverageTerrainHeight_list:
                AverageTerrainHeight_list.append(AverageTerrainHeight)
                
                
        elif "Global Average Altitude" in line:
            AverageAltitude = [float(x) for x in line.split() if is_number_tryexcept(x)][0]
            if AverageAltitude not in AverageAltitude_list:
                AverageAltitude_list.append(AverageAltitude)
                
        elif "Look Direction" in line:
            LookDirection = [str(i) for i in line.split()][-1]
            if LookDirection not in LookDirection_list:
                LookDirection_list.append(LookDirection)
                
    
    #get the image height and width from annotation file
    grd_rows=Lines_list[0]
    grd_cols=Samples_list[0]
    LookDir=LookDirection_list[0]
    PegHeading=PegHeading_list[0]
    PegLatitude=PegLatitude_list[0]
    PegLongitude=PegLongitude_list[0]
    AverageTerrainHeight=AverageTerrainHeight_list[0]
    AverageAltitude=AverageAltitude_list[0]
    
    
    ##the list to be applied
    #PolarimetricList=['T11','T22','T33','T12_real',\
    #                 'T13_imag','T13_real','T23_imag','T23_real','T33']
    #
    ##the imagecollection of the polarimetric data and inc and hgt   
    #PolarimetricCols=ee.ImageCollection('projects/GlobalReservoirs/UAVSAR/UA_neuser_32023_18067_Cols')
    
    ##filter to get the only polarimetric data
    #PolarimetricFilteredImgCols=PolarimetricCols.filterMetadata('name','contains','T')
    
    
    inc_file_name=workstation+"/"+InputDatafolder+"/"+IncFiles
    inc_filenameNoExt=os.path.splitext(os.path.basename(inc_file_name))[0]
    
    IncidenceAngle = ee.Image("projects/GlobalReservoirs/UAVSAR/"+\
                              GeoTiffOutputFolder+"/"+"UA_"+inc_filenameNoExt+"_inc")
    
    
    
#    hgt_file_name=workstation+"/"+InputDatafolder+"/"+hgtFile
#    hgt_filenameNoExt=os.path.splitext(os.path.basename(hgt_file_name))[0]
#    #
#    hgt = ee.Image("projects/GlobalReservoirs/UAVSAR/"+\
#                   GeoTiffOutputFolder+"/"+"UA_"+hgt_filenameNoExt+"_hgt")
    
    #define the peg position /* color: #d63000 */
    peg_Position = ee.Geometry.Point([PegLongitude, PegLatitude])
    
    #the airborne flight height
    FlightHeight=AverageAltitude
    AverageTerrain=AverageTerrainHeight
    
    #if the ascending, then 1, otherwise (if descending) then 0
    AscendingOrNot = 1 if math.cos(math.radians(PegHeading)) > 0 else 0
    
    inc_file_out=workstation+'\\'+GeoTiffOutputFolder+'\\UA_'+\
    os.path.splitext(os.path.basename(IncFiles))[0]+"_inc.tif"
    
    ##############################################################################\\
    ##
    ##             Read information from annotation End                 #\\
    ##                                                                           
    ########################################################################\\
    
    
    
    
    ##############################################################################\\
    ##
    ##             Data processing begin                 #\\
    ##                                                                           
    ########################################################################\\
    
    #get mask of the image
    AngleMask=IncidenceAngle.lt(-100).Not()
    
    #mask the incidence angle
    IncidenceAngleMasked=IncidenceAngle.updateMask(AngleMask)
    
    #get the masked image used for converting to vectors
    BoundoryImageMask=AngleMask.selfMask()
    
    #get the bounds of UAVSAR image
    BoundsVector=BoundoryImageMask.reduceToVectors(reducer=ee.Reducer.countEvery(),
                                                    geometry=IncidenceAngle.geometry(),
                                                    geometryType='polygon',scale=100,
                                                    bestEffort=True).first().geometry()
    
    ##-------------------------------------------------------------
    ##calculate the true azimuth and azimuth flight line
    coords = ee.Array(BoundsVector.coordinates().get(0)).transpose()
    
    #get the corners
    crdLons = ee.List(coords.toList().get(0))
    crdLats = ee.List(coords.toList().get(1))
    minLon = crdLons.sort().get(0)
    maxLon = crdLons.sort().get(-1)
    minLat = crdLats.sort().get(0)
    maxLat = crdLats.sort().get(-1)
    
    #this is based on the corner direction and flight direction
    ## This should be some degree off the North direction(360), due to Earth rotation
    trueAzimuth = ee.Algorithms.If(AscendingOrNot,ee.Number(crdLons.get(crdLats.indexOf(minLat)
    )).subtract(minLon).atan2(ee.Number(crdLats.get(
    crdLons.indexOf(minLon))).subtract(minLat)
    ).multiply(180.0/math.pi).add(270.0),\
    ee.Number(crdLons.get(crdLats.indexOf(minLat))
    ).subtract(minLon).atan2(ee.Number(crdLats.get(
    crdLons.indexOf(minLon))).subtract(minLat)
    ).multiply(180.0/math.pi).add(180.0))
    #print('trueAzimuth',trueAzimuth)
    
    #the geometry setting based on the ascending or descending:
    azimuthEdgeGeometry=ee.Algorithms.If(AscendingOrNot,
            ee.Geometry.LineString([crdLons.get(crdLats.indexOf(maxLat)
            ), maxLat, maxLon, crdLats.get(crdLons.indexOf(maxLon))]),
            ee.Geometry.LineString([crdLons.get(crdLats.indexOf(maxLat)
            ), maxLat,minLon, crdLats.get(crdLons.indexOf(minLon))]))
    #print('azimuthEdgeGeometry',azimuthEdgeGeometry)
    
    azimuthEdgeLine=ee.Feature(ee.Geometry(azimuthEdgeGeometry), {'azimuth': trueAzimuth})
    #print('azimuthEdgeLine',azimuthEdgeLine)
    
    #get the rotation off the north
    rotationFromNorth = ee.Number(trueAzimuth).subtract(360.0)
    #print('rotationFromNorth',rotationFromNorth)
    
    #There will still be some degrees difference 
    #because the s1_inc band is not exactly aligned with the footprint
    #across-range-look-direction 
    #print("True azimuth across-range-look direction", ee.Number(trueAzimuth).subtract(90.0)) 
    
    ##-------------------------------------------------------
    #buffer peg position to have a touch with the image edge
    peg_PositionBuffer=peg_Position.buffer(5000).bounds()
    
    #get the intersection of line and buffer of peg position, 100 is error parameter
    pegBuffer_AzimuthLine_Intersect=azimuthEdgeLine.intersection(peg_PositionBuffer,100)
    
    #get the center point of the two intersect points
    centerPoint=pegBuffer_AzimuthLine_Intersect.centroid()
    #print('centerPoint',centerPoint)
    
    #move the line to new position
    Line_moved = move(azimuthEdgeLine.geometry(), 
    coord_dif(peg_Position,centerPoint.geometry(),0),
    coord_dif(peg_Position,centerPoint.geometry(),1))
    
    #calculate the distance from the flightline to otherside
    distance = ee.FeatureCollection(ee.Feature(Line_moved)).distance()
    
    #get the true theta i which is incidence angle over horizanta
    #theta_i_true=distance.divide(ee.Image.constant(FlightHeight).subtract(
    #        NED_DEM)).atan().multiply(180/math.pi)
    
    theta_iRad = distance.divide(ee.Image.constant(FlightHeight).subtract(
            AverageTerrain)).atan()
    #################radiometric slope correction################
    ##Hoekman, Dirk H., and Johannes Reiche. 
    ##Multi-model radiometric slope correction of SAR images of complex terrain 
    ##using a two-stage semi-empirical approach
    ##Remote Sensing of Environment 156 (2015): 1-10.
    ##Article ( numbers relate to chapters)
    ## 2.1.1 Radar geometry 
    ##note in case the surface is not tilted (i.e. αaz=αr=0), θΔ=θi. 
    #theta_i = theta_i_true
    #
    ##range-look direction
    #phi_i = ee.Number(trueAzimuth).subtract(90.0)
    ##print('phi_i',phi_i)
    #
    ## 2.1.2 Terrain geometry
    #alpha_s = ee.Terrain.slope(hgt).select('slope')
    #
    ###------Big NOTE here ------------------
    ##since here it calculated the downhill direction
    ##we would like to convert it to uphill direction by subtracting 180 degree
    #phi_s = ee.Terrain.aspect(hgt).select('aspect').add(ee.Image.constant(180))
    #
    ## 2.1.3 Model geometry
    ## reduce to 3 angle
    ##if it is ascending, then it should be the slope subtract the range direction
    ## phi_r = ee.Image.constant(phi_i).subtract(phi_s)
    ##if it is descending, it should be the opposite
    #phi_r =ee.Algorithms.If(AscendingOrNot,ee.Image.constant(phi_i).subtract(phi_s),
    #                        phi_s.subtract(ee.Image.constant(phi_i)))
    #
    ## convert all to radians
    #phi_rRad = ee.Image(phi_r).multiply(math.pi/180)
    #alpha_sRad = alpha_s.multiply(math.pi/180)
    #theta_iRad = theta_i.multiply(math.pi/180)
    #ninetyRad = ee.Image.constant(90).multiply(math.pi/180)
    #
    ## slope steepness in range (eq. 2)
    #alpha_r = (alpha_sRad.tan().multiply(phi_rRad.cos())).atan()
    #
    ## slope steepness in azimuth (eq 3)
    #alpha_az = (alpha_sRad.tan().multiply(phi_rRad.sin())).atan()
    #
    
    ##calculate local incidence angle
    #calculateLIA=(alpha_az.cos()).multiply(theta_iRad.subtract(alpha_r).cos()
    #).acos().multiply(180/math.pi)
    #
    ##test
    #calculateIA=alpha_r.add(IncidenceAngle.cos().divide(
    #        alpha_az.cos()).acos()).multiply(180/math.pi)
    
    
    
    ## Volumetric Model
    #nominator = (ninetyRad.subtract(theta_iRad).add(alpha_r)).tan()
    #denominator = (ninetyRad.subtract(theta_iRad)).tan()
    #volModel = (nominator.divide(denominator)).abs()
    
    ###############End radiometric slope correction################
    #################################################################
    
    ###-------------Download Incidence angle----------------------
    ###------------------
    #get the export config parameters
    proj = IncidenceAngleMasked.projection().getInfo()
    
    transform = proj['transform']
    
    crs = IncidenceAngleMasked.projection().crs().getInfo()
    
    #set the export config.
    print(str(grd_cols)+"x"+str(grd_rows))
    taskIA_config=dict(folder='SolarPV',
      fileNamePrefix=InputDatafolder+'_IA',
      crs=crs,
      crsTransform =str(transform),
      dimensions=str(grd_cols)+"x"+str(grd_rows), #"WIDTHxHEIGHT"
      maxPixels=10**13)
     
    
    #export the incidence angle
    taskIA = ee.batch.Export.image.toDrive(
      image=theta_iRad.updateMask(AngleMask),
      description=InputDatafolder+'_IA',**taskIA_config);
        
    #begin task "export image"
    taskIA.start()
    
            
    IA2AssetsId =  "projects/GlobalReservoirs/UAVSAR/"+\
                              GeoTiffOutputFolder+"/"+InputDatafolder+'_IA'
    taskIA2Assets_config=dict(assetId=IA2AssetsId,
      pyramidingPolicy= {'.default': 'mean'},
      crs=crs,
      crsTransform =str(transform),
      dimensions=str(grd_cols)+"x"+str(grd_rows), #"WIDTHxHEIGHT"
      maxPixels=10**13)
            
    #Export to assets
    taskIA2assets = ee.batch.Export.image.toAsset(
    image=theta_iRad.updateMask(AngleMask),
    description=InputDatafolder+'_IA',**taskIA2Assets_config);
        
    #begin task "export image"
#    taskIA2assets.start()
    ###-----End IA Download------------

#workstation='D:\\Data\\UAVSAR'
#InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18069_Cols'
#OutputDataFolder='UA_neuser_32023_18069_Processing'
#
#
#_func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder)
#

    
    
    ###-------------Download Slope Derived from DEM----------------------
#    #set the export config.
#    taskSlope_config=dict(folder='SolarPV',
#      fileNamePrefix=InputDatafolder+'_Slope',
#      crs=crs,
#      crsTransform =str(transform),
#      dimensions=str(grd_cols)+"x"+str(grd_rows), #"WIDTHxHEIGHT"
#      maxPixels=10**13)
     
#    #export the incidence angle
#    taskSlope = ee.batch.Export.image.toDrive(
#      image=alpha_s.updateMask(AngleMask),
#      description=InputDatafolder+'_Slope',**taskSlope_config);
        
    #begin task "export image"
    #taskSlope.start()
    ###-----End Slope Download------------
    
    
    ###-------------Download Slope Derived from DEM----------------------
#    #set the export config.
#    taskAspect_config=dict(folder='SolarPV',
#      fileNamePrefix=InputDatafolder+'_Aspect',
#      crs=crs,
#      crsTransform =str(transform),
#      dimensions=str(grd_cols)+"x"+str(grd_rows), #"WIDTHxHEIGHT"
#      maxPixels=10**13)
#     
#    #export the incidence angle
#    taskAspect = ee.batch.Export.image.toDrive(
#      image=phi_s.updateMask(AngleMask),
#      description=InputDatafolder+'_Aspect',**taskAspect_config);
#        
    #begin task "export image"
    #taskAspect.start()
    
    ###-----End Aspect Download------------
    



