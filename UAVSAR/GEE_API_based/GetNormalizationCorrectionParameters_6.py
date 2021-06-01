"""
######################################################################################################### 
##                                                                                                    #\\
##             UAVSAR Radimetric terrain correction and Radimetric normalization                  #\\
##                                                                                                    #\\
#########################################################################################################
# date: 2019-12-01
# author:  Chao Wang | chao.wang@unc.edu | waynechao128@gmail.com
# Postdoc at the university of North Carolina-Chapel Hill
# Leading by Dr. Tamlin M. Pavelsky for the projects of DEEPP and ABoVE
##--------------------------------------------------------
transfer from the javascript code
#https://code.earthengine.google.com/9fcb622572910bbee371ea3d810ea7b6
"""
import os
import sys
import ee
import math
import re



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

#define function to slice the incidence angle and 
#prepare the parameters for the linear regression model
def splitIncidenceAngleSlicePerDegree(EachTargetAngle):
    startAngle=ee.Number(EachTargetAngle).multiply(math.pi).divide(180.0)
    endAngle=startAngle.add(ee.Number(1*math.pi/180.0))
    #with incidence angle between 50 and 52
    ActSliceMask=theta_iRad.gte(startAngle).And(theta_iRad.lt(endAngle)
    ).And(LC2019.neq(ee.Number(LandTypeValue)))
#    ).And(LC2016.neq(ee.Number(LandTypeValue)))
    
    
    # calculate the mean of sigma for each 1 degree
    meanSigma=GlobalSigma.rename('LN_Sigma').updateMask(ActSliceMask).reduceRegion(
            ee.Reducer.mean(), BoundsVector, 50)
    return ee.Feature(None,{'int':1,'LN_Theta_i':startAngle.log(),\
                            'LN_Sigma':ee.Number(meanSigma.get('LN_Sigma')).abs().log()})


#Function to get the factor for the normlization
def CalculateNormalizationFactor(PolarimetricVariable):
    #define a global variable
    global GlobalSigma
    
    #define the incidence angle range to be considered
    #note here, should not include the angles near the two edges 
    #where the coverage less and are prone to arbitrary error value
    IncidenceAngleListPerDegree = ee.List.sequence(22, 65, 1)
    
    #were converted to sigma-naught
    #since the original data was in db format
    #thus convert it to intensity value first
    GlobalSigma=PolarimetricVariable.updateMask(AngleMask)#.multiply(4*math.pi)
    
    #gamma-naught
    #Gamma0=Sigma.divide(IncidenceAngle.cos())
    #Gamma0=GlobalSigma.divide(theta_i_true.multiply(math.pi/180).cos())
    
    #check the cosine correction based on the Lambert’s law for optics
    # split the incidence angle into many patches per degree and return the mask
    SigmaGammaPerDegree=IncidenceAngleListPerDegree.map(splitIncidenceAngleSlicePerDegree)
    #print('SigmaGammaPerDegree',SigmaGammaPerDegree)
    
    #calculate the slope 
    #The power index, n, is defined as the slope of a linear fit between ln(σ◦θi) and ln(cos θi).
    #σ.θi : Sigma
    #cos θi : theta_i_true.multiply(math.pi/180).cos()
    
    #conduct linear regression operation and get coefficience
    LinearRegsCoeff = ee.FeatureCollection(SigmaGammaPerDegree).reduceColumns(
            ee.Reducer.linearRegression(2,1),['int','LN_Theta_i','LN_Sigma'])
    
    #get slope and intecept of the fitted linear regression model
    LinSlope=ee.Array(LinearRegsCoeff.get('coefficients')).get([1, 0])
    
    #return the factor
    return ee.Feature(AngleMask.geometry(),{'VarName':PolarimetricVariable.get('name'),
                            'LinearSlope':LinSlope})
    
###-----------End Functions defination-------------------------------



######################################################################################################### 
##                                                                                                    #\\
##              User Input Parameters                  #\\
##                                                                                                    #\\
#########################################################################################################

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


##define the peg position /* color: #d63000 */
#peg_Position = ee.Geometry.Point([-76.829877711, 35.159781495])
#
##the airborne flight height
#FlightHeight=12499.6

#if the ascending, then 1, otherwise (if descending) then 0
#AscendingOrNot =1

#NED_DEM = ee.Image("USGS/NED")  
#NED_DEM=hgt#ee.Image('USGS/SRTMGL1_003') 


####-----------End User Input Parameters-------------------------------------
    
def _func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder):
    global LC2016
    global LC2019
    global LandTypeValue
    global theta_iRad
    global BoundsVector
    global AngleMask
    
    #init the earthengine api
    ee.Initialize()
    
#    #get land cover dataset
#    NLCD2016 = ee.Image("USGS/NLCD/NLCD2016")
#    LC2016=NLCD2016.select('landcover')
#    
#    #41,42,43 forest
#    #82 crop
#    #11 water
#    LandTypeValue=11#82#41#42#43#7,8,9
    
    
    LC2019= ee.Image(ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V-C3/Global")\
    .filterDate('2019-01-01','2020-01-01').first()).select(['discrete_classification'])\
#    .eq(ee.Image.constant(80));
    #80 water
    LandTypeValue=80

    
    # read some header file
    # Empty lists to put information that will be recalled later.
    grdFiles_List=[]
    Lines_list = []
    
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
       
    #here this image will be used as a mask file
    ImgUsedAsMask = ee.Image("projects/GlobalReservoirs/UAVSAR/"+\
                              GeoTiffOutputFolder+"/" + InputDatafolder + \
                              "_D_Freeman_Dbl")
    
    
    IncidenceAngle = ee.Image("projects/GlobalReservoirs/UAVSAR/"+\
                              GeoTiffOutputFolder+"/"+InputDatafolder+"_IA")
    
    #set the incidence angle
    #please make sure this incidence angle is Rad
#    theta_iRad=IncidenceAngle
    theta_iRad=IncidenceAngle.multiply(math.pi).divide(180.0)
#    print('IncidenceAngle',IncidenceAngle.getInfo())
    ####--------End header file read
    
    
    ##############################################################################\\
    ##
    ##             Data processing begin                 #\\
    ##                                                                           
    ########################################################################\\
    
    #the list to be applied
    PolarimetricList=['alpha','anisotropy','entropy','lambda',\
                     'Freeman_Dbl','Freeman_Odd','Freeman_Vol']
    
    #the imagecollection of the polarimetric data and inc and hgt   
    PolarimetricImgCols=ee.ImageCollection('projects/GlobalReservoirs/UAVSAR/' + GeoTiffOutputFolder)
    
    #filter to get the only polarimetric data
    PolorizationImgCols=PolarimetricImgCols.filterMetadata('name','contains','P_')
    
    #filter to get the decomposition data
    PolDecompositesImgCols=PolarimetricImgCols.filterMetadata('name','contains','D_')
    
    #since I don;t need to use the pauli data for any further processing locally
    #I will just filter it out
    OtherPolDecomImgCols=PolDecompositesImgCols.\
    filterMetadata('name','not_contains','D_pauli')
    #print('PolarimetricFilteredImgCols',PolarimetricFilteredImgCols.getInfo())
    
    #filter to get the decomposite variable
    PauliDecompElement=PolDecompositesImgCols.\
    filterMetadata('name','contains','D_pauli')
    
    #rearrange the Pauli image as imagecols
    PauliImgCols=ee.ImageCollection.\
    fromImages([ee.Image(PauliDecompElement.first()).\
                select([0],['D_pauli1']).set('name', 'D_pauli1'),
                ee.Image(PauliDecompElement.first()).\
                select([1],['D_pauli2']).set('name', 'D_pauli2'),
                ee.Image(PauliDecompElement.first()).\
                select([2],['D_pauli3']).set('name', 'D_pauli3')])
    
    #print('PauliImgCols',PauliImgCols.getInfo())
    
    #Combine the polarization and decomposition ImgCollection
    PolarMetricImgCols=PolorizationImgCols.merge(OtherPolDecomImgCols).merge(PauliImgCols);
#    print('PauliImgCols',PolarMetricImgCols.getInfo())
#    PolarMetricImgCols=PolDecompositesImgCols;
    
    #get mask of the image
#    AngleMask=LocIncidenceAngle.lt(-100).Not()
    AngleMask=ImgUsedAsMask.neq(0)
    
    #get the masked image used for converting to vectors
    BoundoryImageMask=AngleMask.selfMask()
    
    #get the bounds of UAVSAR image
    BoundsVector=BoundoryImageMask.reduceToVectors(reducer=ee.Reducer.countEvery(),
                                                    geometry=ImgUsedAsMask.geometry(),
                                                    geometryType='polygon',scale=100,
                                                    bestEffort=True).first().geometry()
    
    
    ###############End radiometric slope correction################
    #################################################################
    RadMetricNormFactors=PolarMetricImgCols.map(CalculateNormalizationFactor)
        
    #export the factor
    taskRadNormFactorsTableToDrive = ee.batch.Export.table.toDrive(
        collection=RadMetricNormFactors,
        description=GeoTiffOutputFolder+'RadNormFactors',
        folder='SolarPV',
        fileNamePrefix=GeoTiffOutputFolder+'RadNormFactors') 
    
    #begin task "export table"
    taskRadNormFactorsTableToDrive.start()
    
    #export the factor into asset
    TableAssetID="projects/GlobalReservoirs/UAVSAR/"+\
    GeoTiffOutputFolder+'RadNormFactors'
    
    taskRadNormFactorsTableToAsset = ee.batch.Export.table.toAsset(
        collection=RadMetricNormFactors,
        description=GeoTiffOutputFolder+'RadNormFactors',
        assetId=TableAssetID) 
    
    #begin task "export table"
    taskRadNormFactorsTableToAsset.start()



#workstation='D:\\Data\\UAVSAR'
#InputDatafolder='UA_neuser_32023_18069_002_180923_L090_CX_01'
#GeoTiffOutputFolder='UA_neuser_32023_18069_Cols'
#OutputDataFolder='UA_neuser_32023_18069_Processing'
#
#
##InputDatafolder='UA_neuser_32023_18065_002_180918_L090_CX_01'
##GeoTiffOutputFolder='UA_neuser_32023_18065_Cols'
##OutputDataFolder='UA_neuser_32023_18065_Processing'
#
#
#_func(workstation,InputDatafolder,GeoTiffOutputFolder,OutputDataFolder)


###----------------------Code backup-----------------------------
###-------------------------------------------------------------
###calculate the true azimuth and azimuth flight line
#coords = ee.Array(BoundsVector.coordinates().get(0)).transpose()
#
##get the corners
#crdLons = ee.List(coords.toList().get(0))
#crdLats = ee.List(coords.toList().get(1))
#minLon = crdLons.sort().get(0)
#maxLon = crdLons.sort().get(-1)
#minLat = crdLats.sort().get(0)
#maxLat = crdLats.sort().get(-1)
#
##this is based on the corner direction and flight direction
### This should be some degree off the North direction(360), due to Earth rotation
#trueAzimuth = ee.Algorithms.If(AscendingOrNot,ee.Number(crdLons.get(crdLats.indexOf(minLat)
#)).subtract(minLon).atan2(ee.Number(crdLats.get(
#crdLons.indexOf(minLon))).subtract(minLat)
#).multiply(180.0/math.pi).add(270.0),\
#ee.Number(crdLons.get(crdLats.indexOf(minLat))
#).subtract(minLon).atan2(ee.Number(crdLats.get(
#crdLons.indexOf(minLon))).subtract(minLat)
#).multiply(180.0/math.pi).add(180.0))
##print('trueAzimuth',trueAzimuth)
#
##the geometry setting based on the ascending or descending:
#azimuthEdgeGeometry=ee.Algorithms.If(AscendingOrNot,
#        ee.Geometry.LineString([crdLons.get(crdLats.indexOf(maxLat)
#        ), maxLat, maxLon, crdLats.get(crdLons.indexOf(maxLon))]),
#        ee.Geometry.LineString([crdLons.get(crdLats.indexOf(maxLat)
#        ), maxLat,minLon, crdLats.get(crdLons.indexOf(minLon))]))
##print('azimuthEdgeGeometry',azimuthEdgeGeometry)
#
#azimuthEdgeLine=ee.Feature(ee.Geometry(azimuthEdgeGeometry), {'azimuth': trueAzimuth})
##print('azimuthEdgeLine',azimuthEdgeLine)
#
##get the rotation off the north
#rotationFromNorth = ee.Number(trueAzimuth).subtract(360.0)
##print('rotationFromNorth',rotationFromNorth)
#
##There will still be some degrees difference 
##because the s1_inc band is not exactly aligned with the footprint
##across-range-look-direction 
##print("True azimuth across-range-look direction", ee.Number(trueAzimuth).subtract(90.0)) 
#
###-------------------------------------------------------
##buffer peg position to have a touch with the image edge
#peg_PositionBuffer=peg_Position.buffer(5000).bounds()
#
##get the intersection of line and buffer of peg position, 100 is error parameter
#pegBuffer_AzimuthLine_Intersect=azimuthEdgeLine.intersection(peg_PositionBuffer,100)
#
##get the center point of the two intersect points
#centerPoint=pegBuffer_AzimuthLine_Intersect.centroid()
##print('centerPoint',centerPoint)
#
##move the line to new position
#Line_moved = move(azimuthEdgeLine.geometry(), 
#coord_dif(peg_Position,centerPoint.geometry(),0),
#coord_dif(peg_Position,centerPoint.geometry(),1))
#
##calculate the distance from the flightline to otherside
#distance = ee.FeatureCollection(ee.Feature(Line_moved)).distance()
#
##get the true theta i which is incidence angle over horizanta
##theta_i_true=distance.divide(ee.Image.constant(FlightHeight).subtract(
##        NED_DEM)).atan().multiply(180/math.pi)
#
#theta_iRad = distance.divide(ee.Image.constant(FlightHeight).subtract(
#        NED_DEM)).atan()
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
#alpha_s = ee.Terrain.slope(NED_DEM).select('slope')
#
###------Big NOTE here ------------------
##since here it calculated the downhill direction
##we would like to convert it to uphill direction by subtracting 180 degree
#phi_s = ee.Terrain.aspect(NED_DEM).select('aspect').add(ee.Image.constant(180))
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
