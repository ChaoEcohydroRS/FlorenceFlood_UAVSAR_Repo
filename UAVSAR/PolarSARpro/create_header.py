
# -*- coding: utf-8 -*-
"""
Spyder Editor
@author: Daniel Jensen, danieljohnjensen@gmail.com
Scott Baron,Jwely
revised by wayne
"""
import os
import re
 

def create_INC_header(folder):
    print('create_INC_header!')
    """
    Builds a header file for the input UAVSAR .grd file,
    allowing the data to be read as a raster dataset.

    :param folder:   the folder containing the UAVSAR .grd and .ann files
    """

    os.chdir(folder)

    # Empty lists to put information that will be recalled later.
    Lines_list = []
    Samples_list = []
    Latitude_list = []
    Longitude_list = []
    LatitudeSpace_list=[]
    LongitudeSpace_list=[]
    Files_list = []

    # Step 1: Look through folder and determine how many different flights there are
    # by looking at the HDR files.
    for files in os.listdir(folder):
#        if files [-4:] == ".grd":
        if files [-4:] == ".inc":
            newfile = open(files[0:-4] + ".hdr", 'w')
            newfile.writelines(
                """
                ENVI
                description = {DESCFIELD}
                samples = NSAMP
                lines   = NLINE
                bands   = 1
                header offset = 0
                file type = ENVI Standard
                data type = DATTYPE
                interleave = bsq
                sensor type = Unknown
                byte order = 0
                map info = {
                        Geographic Lat/Lon,
                        1.000, 1.000,
                        LONGITUDE,
                        LATITUDE,
                        LonSpace,
                        LatSpace,
                        WGS-84,
                        units=Degrees
                        }
                coordinate system string = {
                        GEOGCS["GCS_WGS_1984",
                            DATUM["D_WGS_1984",
                            SPHEROID["WGS_1984",
                            6378137.0,298.257223563]],
                        PRIMEM["Greenwich",0],
                        UNIT["Degree",0.017453292519943295]]
                        }
                wavelength units = Unknown
                """
                          )
            newfile.close()
            if files[0:18] not in Files_list:
                Files_list.append(files[0:18])

    #Variables used to recall indexed values.
    var1 = 0

    #Step 2: Look through the folder and locate the annotation file(s).
    # These can be in either .txt or .ann file types.
    for files in os.listdir(folder):
        if Files_list[var1] and files[-4:] == ".txt" or files[-4:] == ".ann":
            #Step 3: Once located, find the info we are interested in and append it to
            # the appropriate list. We limit the variables to <=1 so that they only
            # return two values (one for each polarization of
            searchfile = open(files, "r")
            for line in searchfile:
#                if "GRD Lines" in line:
                if "INC Lines" in line:
                    Lines = [int(i) for i in line.split() if i.isdigit()][0]
#                    Lines = line[55:60]
                    if Lines not in Lines_list:
                        Lines_list.append(Lines)

                elif "INC Samples" in line:
#                elif "GRD Samples" in line:
                    Samples = [int(i) for i in line.split() if i.isdigit()][0]
#                    Samples = line[55:60]
                    if Samples not in Samples_list:
                        Samples_list.append(Samples)

#                elif "grd_mag.row_addr" in line:
                elif "inc.row_addr" in line:                     
                    Latitude = line.split()[3]
                    print(Latitude)
                    if Latitude not in Latitude_list:
                        Latitude_list.append(Latitude)

#                elif "grd_mag.col_addr" in line: 
                elif "inc.col_addr" in line:
                    Longitude = line.split()[3]
                    print(Longitude)
                    if Longitude not in Longitude_list:
                        Longitude_list.append(Longitude)
                        
                #INC Longitude Pixel Spacing
                elif "inc.col_mult" in line:
                    LongitudeSpace = abs(float(line.split()[3]))
                    print(LongitudeSpace)
                    if LongitudeSpace not in LongitudeSpace_list:
                        LongitudeSpace_list.append(LongitudeSpace)
                
                #INC Latitude Pixel Spacing      
                elif "inc.row_mult" in line:
                    LatitudeSpace = abs(float(line.split()[3]))
                    print(LatitudeSpace)
                    if LatitudeSpace not in LatitudeSpace_list:
                        LatitudeSpace_list.append(LatitudeSpace)
            #Reset the variables to zero for each different flight date.
            var1 = 0
            searchfile.close()

    #var6 = 0

    # Step 3: Open HDR file and replace data.
    for files in os.listdir(folder):
        if files[-4:] == ".hdr":
            with open(files, "r") as sources:
                lines = sources.readlines()
            with open(files, "w") as sources:
                for line in lines:
                    if "data type = DATTYPE" in line:
#                        sources.write(re.sub(line[12:19], "4", line))
                        sources.write(re.sub("DATTYPE", "4",line).lstrip())
                    elif "DESCFIELD" in line:
                        sources.write(re.sub("DESCFIELD", "File Imported into ENVI.",line).lstrip())
#                        sources.write(re.sub(line[2:11], "", line))
                    elif "lines" in line:
                        sources.write(re.sub("NLINE", str(Lines_list[0]),line).lstrip())
#                        sources.write(re.sub(line[10:15], Lines_list[Files_list.index(files[0:18])], line))
                    elif "samples" in line:
                        sources.write(re.sub("NSAMP", str(Samples_list[0]),line).lstrip())
#                        sources.write(re.sub(line[10:15], Samples_list[Files_list.index(files[0:18])], line))
                    elif "LONGITUDE" in line:
                        sources.write(re.sub("LONGITUDE", str(Longitude_list[0]),line).lstrip())
                    
                    elif "LATITUDE" in line:
                        sources.write(re.sub("LATITUDE", str(Latitude_list[0]),line).lstrip())
                        
                    elif "LonSpace" in line:
                        sources.write(re.sub("LonSpace", str(LongitudeSpace_list[0]),line).lstrip())
                    
                    elif "LatSpace" in line:
                        sources.write(re.sub("LatSpace", str(LatitudeSpace_list[0]),line).lstrip())
                        
#                    elif "map info" in line:
#                        sources.write(re.sub(line[47:66], "{lon}, {lat}".format(
#                                                    lon=Longitude_list[Files_list.index(files[0:18])],
#                                                    lat=Latitude_list[Files_list.index(files[0:18])]), line))
                    else:
                        sources.write(line.lstrip())

    print("Finished creating hdrs")
    return

def create_grd_header(folder,annfolder):
    """
    Builds a header file for the input UAVSAR .grd file,
    allowing the data to be read as a raster dataset.

    :param folder:   the folder containing the UAVSAR .grd and .ann files
    """

    os.chdir(folder)

    # Empty lists to put information that will be recalled later.
    Lines_list = []
    Samples_list = []
    Latitude_list = []
    Longitude_list = []
    LatitudeSpace_list=[]
    LongitudeSpace_list=[]
    Files_list = []
    

    # Step 1: Look through folder and determine how many different flights there are
    # by looking at the HDR files.
    for files in os.listdir(folder):
        if files [-4:] == ".grd":
            newfile = open(files[0:-4] + ".hdr", 'w')
            newfile.writelines(
                """
                ENVI
                description = {DESCFIELD}
                samples = NSAMP
                lines   = NLINE
                bands   = BandNum
                header offset = 0
                file type = ENVI Standard
                data type = DATTYPE
                interleave = bsqOrBip
                sensor type = Unknown
                byte order = 0
                map info = {
                        Geographic Lat/Lon,
                        1.000, 1.000,
                        LONGITUDE,
                        LATITUDE,
                        LonSpace,
                        LatSpace,
                        WGS-84,
                        units=Degrees
                        }
                coordinate system string = {
                        GEOGCS["GCS_WGS_1984",
                            DATUM["D_WGS_1984",
                            SPHEROID["WGS_1984",
                            6378137.0,298.257223563]],
                        PRIMEM["Greenwich",0],
                        UNIT["Degree",0.017453292519943295]]
                        }
                wavelength units = Unknown
                """
                          )
            newfile.close()
            if files[0:18] not in Files_list:
                Files_list.append(files[0:18])

    #Variables used to recall indexed values.
    var1 = 0

    #Step 2: Look through the folder and locate the annotation file(s).
    # These can be in either .txt or .ann file types.
    for files in os.listdir(folder):
        if Files_list[var1] and files[-4:] == ".txt" or files[-4:] == ".ann":
            #Step 3: Once located, find the info we are interested in and append it to
            # the appropriate list. We limit the variables to <=1 so that they only
            # return two values (one for each polarization of
            searchfile = open(files, "r")
            for line in searchfile:
                if "GRD Lines" in line:
                    Lines = [int(i) for i in line.split() if i.isdigit()][0]
#                    Lines = line[55:60]
                    if Lines not in Lines_list:
                        Lines_list.append(Lines)


                elif "GRD Samples" in line:
                    Samples = [int(i) for i in line.split() if i.isdigit()][0]
#                    Samples = line[55:60]
                    if Samples not in Samples_list:
                        Samples_list.append(Samples)

                elif "grd_mag.row_addr" in line:                  
                    Latitude = line.split()[3]
                    print(Latitude)
                    if Latitude not in Latitude_list:
                        Latitude_list.append(Latitude)

                elif "grd_mag.col_addr" in line:
                    Longitude = line.split()[3]
                    print(Longitude)
                    if Longitude not in Longitude_list:
                        Longitude_list.append(Longitude)
                        
                #GRD Longitude Pixel Spacing
                elif "grd_mag.col_mult" in line:
                    LongitudeSpace = abs(float(line.split()[3]))
                    print(LongitudeSpace)
                    if LongitudeSpace not in LongitudeSpace_list:
                        LongitudeSpace_list.append(LongitudeSpace)
                
                #GRD Latitude Pixel Spacing      
                elif "grd_mag.row_mult" in line:
                    LatitudeSpace = abs(float(line.split()[3]))
                    print(LatitudeSpace)
                    if LatitudeSpace not in LatitudeSpace_list:
                        LatitudeSpace_list.append(LatitudeSpace)
            #Reset the variables to zero for each different flight date.
            var1 = 0
            searchfile.close()

    #var6 = 0

    # Step 3: Open HDR file and replace data.
    for files in os.listdir(folder):
        if files[-4:] == ".hdr":
            with open(files, "r") as sources:
                lines = sources.readlines()
            with open(files, "w") as sources:
                for line in lines:
                    if "data type = DATTYPE" in line:
#                        sources.write(re.sub(line[12:19], "4", line))
                        sources.write(re.sub("DATTYPE", "4",line).lstrip())
                    elif "DESCFIELD" in line:
                        sources.write(re.sub("DESCFIELD", "File Imported into ENVI.",line).lstrip())
#                        sources.write(re.sub(line[2:11], "", line))
                    elif "lines" in line:
                        sources.write(re.sub("NLINE", str(Lines_list[0]),line).lstrip())
#                        sources.write(re.sub(line[10:15], Lines_list[Files_list.index(files[0:18])], line))
                    elif "samples" in line:
                        sources.write(re.sub("NSAMP", str(Samples_list[0]),line).lstrip())
                    elif "bands" in line:
                        if files[-14:-10] in ['HHHV', 'HHVV', 'HVVV']:
                            sources.write(re.sub("BandNum", "2",line).lstrip())
                        elif files[-14:-10] in ['HHHH', 'HVHV', 'VVVV']:
                            sources.write(re.sub("BandNum", "1",line).lstrip())
                    elif "interleave" in line:
                        if files[-14:-10] in ['HHHV', 'HHVV', 'HVVV']:
                            sources.write(re.sub("bsqOrBip", "bip",line).lstrip())
                        elif files[-14:-10] in ['HHHH', 'HVHV', 'VVVV']:
                            sources.write(re.sub("bsqOrBip", "bsq",line).lstrip())     
                    elif "LONGITUDE" in line:
                        sources.write(re.sub("LONGITUDE", str(Longitude_list[0]),line).lstrip())
                    
                    elif "LATITUDE" in line:
                        sources.write(re.sub("LATITUDE", str(Latitude_list[0]),line).lstrip())
                        
                    elif "LonSpace" in line:
                        sources.write(re.sub("LonSpace", str(LongitudeSpace_list[0]),line).lstrip())
                    
                    elif "LatSpace" in line:
                        sources.write(re.sub("LatSpace", str(LatitudeSpace_list[0]),line).lstrip())
 
                        
#                    elif "map info" in line:
#                        sources.write(re.sub(line[47:66], "{lon}, {lat}".format(
#                                                    lon=Longitude_list[Files_list.index(files[0:18])],
#                                                    lat=Latitude_list[Files_list.index(files[0:18])]), line))
                    else:
                        sources.write(line.lstrip())

    print("Finished creating hdrs")
    return

def create_hgt_header(folder):
    """
    Builds a header file for the input UAVSAR .grd file,
    allowing the data to be read as a raster dataset.

    :param folder:   the folder containing the UAVSAR .grd and .ann files
    """

    os.chdir(folder)

    # Empty lists to put information that will be recalled later.
    Lines_list = []
    Samples_list = []
    Latitude_list = []
    Longitude_list = []
    Files_list = []
    LongitudeSpace_list=[]
    LatitudeSpace_list=[]

    # Step 1: Look through folder and determine how many different flights there are
    # by looking at the HDR files.
    for files in os.listdir(folder):
#        if files [-4:] == ".grd":
        if files [-4:] == ".inc":
            newfile = open(files[0:-4] + ".hdr", 'w')
            newfile.writelines(
                """
                ENVI
                description = {DESCFIELD}
                samples = NSAMP
                lines   = NLINE
                bands   = 1
                header offset = 0
                file type = ENVI Standard
                data type = DATTYPE
                interleave = bsq
                sensor type = Unknown
                byte order = 0
                map info = {
                        Geographic Lat/Lon,
                        1.000, 1.000,
                        LONGITUDE,
                        LATITUDE,
                        LonSpace,
                        LatSpace,
                        WGS-84,
                        units=Degrees
                        }
                coordinate system string = {
                        GEOGCS["GCS_WGS_1984",
                            DATUM["D_WGS_1984",
                            SPHEROID["WGS_1984",
                            6378137.0,298.257223563]],
                        PRIMEM["Greenwich",0],
                        UNIT["Degree",0.017453292519943295]]
                        }
                wavelength units = Unknown
                """
                          )
            newfile.close()
            if files[0:18] not in Files_list:
                Files_list.append(files[0:18])

    #Variables used to recall indexed values.
    var1 = 0

    #Step 2: Look through the folder and locate the annotation file(s).
    # These can be in either .txt or .ann file types.
    for files in os.listdir(folder):
        if Files_list[var1] and files[-4:] == ".txt" or files[-4:] == ".ann":
            #Step 3: Once located, find the info we are interested in and append it to
            # the appropriate list. We limit the variables to <=1 so that they only
            # return two values (one for each polarization of
            searchfile = open(files, "r")
            for line in searchfile:
#                if "GRD Lines" in line:
                if "INC Lines" in line:
                    Lines = [int(i) for i in line.split() if i.isdigit()][0]
#                    Lines = line[55:60]
                    if Lines not in Lines_list:
                        Lines_list.append(Lines)

                elif "INC Samples" in line:
#                elif "GRD Samples" in line:
                    Samples = [int(i) for i in line.split() if i.isdigit()][0]
#                    Samples = line[55:60]
                    if Samples not in Samples_list:
                        Samples_list.append(Samples)

#                elif "grd_mag.row_addr" in line:
                elif "inc.row_addr" in line:                     
                    Latitude = line.split()[3]
                    print(Latitude)
                    if Latitude not in Latitude_list:
                        Latitude_list.append(Latitude)

#                elif "grd_mag.col_addr" in line:
                elif "inc.col_addr" in line:
                    Longitude = line.split()[3]
                    print(Longitude)
                    if Longitude not in Longitude_list:
                        Longitude_list.append(Longitude)
                        
                #INC Longitude Pixel Spacing
                elif "inc.col_mult" in line:
                    LongitudeSpace = abs(float(line.split()[3]))
                    print(LongitudeSpace)
                    if LongitudeSpace not in LongitudeSpace_list:
                        LongitudeSpace_list.append(LongitudeSpace)
                
                #INC Latitude Pixel Spacing      
                elif "inc.row_mult" in line:
                    LatitudeSpace = abs(float(line.split()[3]))
                    print(LatitudeSpace)
                    if LatitudeSpace not in LatitudeSpace_list:
                        LatitudeSpace_list.append(LatitudeSpace)                        
            #Reset the variables to zero for each different flight date.
            var1 = 0
            searchfile.close()

    #var6 = 0

    # Step 3: Open HDR file and replace data.
    for files in os.listdir(folder):
        if files[-4:] == ".hdr":
            with open(files, "r") as sources:
                lines = sources.readlines()
            with open(files, "w") as sources:
                for line in lines:
                    if "data type = DATTYPE" in line:
#                        sources.write(re.sub(line[12:19], "4", line))
                        sources.write(re.sub("DATTYPE", "4",line).lstrip())
                    elif "DESCFIELD" in line:
                        sources.write(re.sub("DESCFIELD", "File Imported into ENVI.",line).lstrip())
#                        sources.write(re.sub(line[2:11], "", line))
                    elif "lines" in line:
                        sources.write(re.sub("NLINE", str(Lines_list[0]),line).lstrip())
#                        sources.write(re.sub(line[10:15], Lines_list[Files_list.index(files[0:18])], line))
                    elif "samples" in line:
                        sources.write(re.sub("NSAMP", str(Samples_list[0]),line).lstrip())
#                        sources.write(re.sub(line[10:15], Samples_list[Files_list.index(files[0:18])], line))
                    elif "LONGITUDE" in line:
                        sources.write(re.sub("LONGITUDE", str(Longitude_list[0]),line).lstrip())
                    
                    elif "LATITUDE" in line:
                        sources.write(re.sub("LATITUDE", str(Latitude_list[0]),line).lstrip())
                        
                    elif "LonSpace" in line:
                        sources.write(re.sub("LonSpace", str(LongitudeSpace_list[0]),line).lstrip())
                    
                    elif "LatSpace" in line:
                        sources.write(re.sub("LatSpace", str(LatitudeSpace_list[0]),line).lstrip())
                        
#                    elif "map info" in line:
#                        sources.write(re.sub(line[47:66], "{lon}, {lat}".format(
#                                                    lon=Longitude_list[Files_list.index(files[0:18])],
#                                                    lat=Latitude_list[Files_list.index(files[0:18])]), line))
                    else:
                        sources.write(line.lstrip())

    print("Finished creating hdrs")
    return


def create_bin_header(folder,annfolder):
    """
    Builds a header file for the input UAVSAR .grd file,
    allowing the data to be read as a raster dataset.

    :param folder:   the folder containing the UAVSAR .grd and .ann files
    """

    os.chdir(folder)

    # Empty lists to put information that will be recalled later.
    Lines_list = []
    Samples_list = []
    Latitude_list = []
    Longitude_list = []
    Files_list = []
    LongitudeSpace_list=[]
    LatitudeSpace_list=[]

    # Step 1: Look through folder and determine how many different flights there are
    # by looking at the HDR files.
    for files in os.listdir(folder):
#        if files [-4:] == ".grd":
        if files [-4:] == ".bin":
            newfile = open(files[0:-4] + ".hdr", 'w')
            newfile.writelines(
                """
                ENVI
                description = {DESCFIELD}
                samples = NSAMP
                lines   = NLINE
                bands   = 1
                header offset = 0
                file type = ENVI Standard
                data type = DATTYPE
                interleave = bsq
                sensor type = Unknown
                byte order = 0
                map info = {
                        Geographic Lat/Lon,
                        1.000, 1.000,
                        LONGITUDE,
                        LATITUDE,
                        LonSpace,
                        LatSpace,
                        WGS-84,
                        units=Degrees
                        }
                coordinate system string = {
                        GEOGCS["GCS_WGS_1984",
                            DATUM["D_WGS_1984",
                            SPHEROID["WGS_1984",
                            6378137.0,298.257223563]],
                        PRIMEM["Greenwich",0],
                        UNIT["Degree",0.017453292519943295]]
                        }
                wavelength units = Unknown
                """
                          )
            newfile.close()
            if files[0:18] not in Files_list:
                Files_list.append(files[0:18])

    #Variables used to recall indexed values.
    var1 = 0

    #Step 2: Look through the folder and locate the annotation file(s).
    # These can be in either .txt or .ann file types.
    for files in os.listdir(annfolder):
        if Files_list[var1] and files[-4:] == ".txt" or files[-4:] == ".ann":
            #Step 3: Once located, find the info we are interested in and append it to
            # the appropriate list. We limit the variables to <=1 so that they only
            # return two values (one for each polarization of
            searchfile = open(annfolder+files, "r")
            for line in searchfile:
#                if "GRD Lines" in line:
                if "INC Lines" in line:
                    Lines = [int(i) for i in line.split() if i.isdigit()][0]
#                    Lines = line[55:60]
                    if Lines not in Lines_list:
                        Lines_list.append(Lines)

                elif "INC Samples" in line:
#                elif "GRD Samples" in line:
                    Samples = [int(i) for i in line.split() if i.isdigit()][0]
#                    Samples = line[55:60]
                    if Samples not in Samples_list:
                        Samples_list.append(Samples)

#                elif "grd_mag.row_addr" in line:
                elif "inc.row_addr" in line:                     
                    Latitude = line.split()[3]
                    print(Latitude)
                    if Latitude not in Latitude_list:
                        Latitude_list.append(Latitude)

#                elif "grd_mag.col_addr" in line:
                elif "inc.col_addr" in line:
                    Longitude = line.split()[3]
                    print(Longitude)
                    if Longitude not in Longitude_list:
                        Longitude_list.append(Longitude)
                        
                #INC Longitude Pixel Spacing
                elif "inc.col_mult" in line:
                    LongitudeSpace = abs(float(line.split()[3]))
                    print(LongitudeSpace)
                    if LongitudeSpace not in LongitudeSpace_list:
                        LongitudeSpace_list.append(LongitudeSpace)
                
                #INC Latitude Pixel Spacing      
                elif "inc.row_mult" in line:
                    LatitudeSpace = abs(float(line.split()[3]))
                    print(LatitudeSpace)
                    if LatitudeSpace not in LatitudeSpace_list:
                        LatitudeSpace_list.append(LatitudeSpace)    
            #Reset the variables to zero for each different flight date.
            var1 = 0
            searchfile.close()

    #var6 = 0

    # Step 3: Open HDR file and replace data.
    for files in os.listdir(folder):
        if files[-4:] == ".hdr":
            with open(files, "r") as sources:
                lines = sources.readlines()
            with open(files, "w") as sources:
                for line in lines:
                    if "data type = DATTYPE" in line:
#                        sources.write(re.sub(line[12:19], "4", line))
                        sources.write(re.sub("DATTYPE", "4",line).lstrip())
                    elif "DESCFIELD" in line:
                        sources.write(re.sub("DESCFIELD", "File Imported into ENVI.",line).lstrip())
#                        sources.write(re.sub(line[2:11], "", line))
                    elif "lines" in line:
                        sources.write(re.sub("NLINE", str(Lines_list[0]),line).lstrip())
#                        sources.write(re.sub(line[10:15], Lines_list[Files_list.index(files[0:18])], line))
                    elif "samples" in line:
                        sources.write(re.sub("NSAMP", str(Samples_list[0]),line).lstrip())
#                        sources.write(re.sub(line[10:15], Samples_list[Files_list.index(files[0:18])], line))
                    elif "LONGITUDE" in line:
                        sources.write(re.sub("LONGITUDE", str(Longitude_list[0]),line).lstrip())
                    
                    elif "LATITUDE" in line:
                        sources.write(re.sub("LATITUDE", str(Latitude_list[0]),line).lstrip())
                        
                    elif "LonSpace" in line:
                        sources.write(re.sub("LonSpace", str(LongitudeSpace_list[0]),line).lstrip())
                    
                    elif "LatSpace" in line:
                        sources.write(re.sub("LatSpace", str(LatitudeSpace_list[0]),line).lstrip())
                        
#                    elif "map info" in line:
#                        sources.write(re.sub(line[47:66], "{lon}, {lat}".format(
#                                                    lon=Longitude_list[Files_list.index(files[0:18])],
#                                                    lat=Latitude_list[Files_list.index(files[0:18])]), line))
                    else:
                        sources.write(line.lstrip())

    print("Finished creating hdrs")
    return


#
def create_bmp_header(folder,annfolder):
    """
    Builds a header file for the input UAVSAR .grd file,
    allowing the data to be read as a raster dataset.

    :param folder:   the folder containing the UAVSAR .grd and .ann files
    """

    os.chdir(folder)

    # Empty lists to put information that will be recalled later.
    Lines_list = []
    Samples_list = []
    Latitude_list = []
    Longitude_list = []
    Files_list = []
    LongitudeSpace_list=[]
    LatitudeSpace_list=[]

    # Step 1: Look through folder and determine how many different flights there are
    # by looking at the HDR files.
    for files in os.listdir(folder):
#        if files [-4:] == ".grd":
        if files [-4:] == ".bmp":
            newfile = open(files[0:-4] + ".hdr", 'w')
            newfile.writelines(
                """
                ENVI
                description = {DESCFIELD}
                samples = NSAMP
                lines   = NLINE
                bands   = 3
                header offset = 0
                file type = ENVI Standard
                data type = DATTYPE
                interleave = bsq
                sensor type = Unknown
                byte order = 0
                map info = {
                        Geographic Lat/Lon,
                        1.000, 1.000,
                        LONGITUDE,
                        LATITUDE,
                        LonSpace,
                        LatSpace,
                        WGS-84,
                        units=Degrees
                        }
                coordinate system string = {
                        GEOGCS["GCS_WGS_1984",
                            DATUM["D_WGS_1984",
                            SPHEROID["WGS_1984",
                            6378137.0,298.257223563]],
                        PRIMEM["Greenwich",0],
                        UNIT["Degree",0.017453292519943295]]
                        }
                wavelength units = Unknown
                """
                          )
            newfile.close()
            if files[0:18] not in Files_list:
                Files_list.append(files[0:18])

    #Variables used to recall indexed values.
    var1 = 0

    #Step 2: Look through the folder and locate the annotation file(s).
    # These can be in either .txt or .ann file types.
    for files in os.listdir(annfolder):
        if Files_list[var1] and files[-4:] == ".txt" or files[-4:] == ".ann":
            #Step 3: Once located, find the info we are interested in and append it to
            # the appropriate list. We limit the variables to <=1 so that they only
            # return two values (one for each polarization of
            searchfile = open(annfolder+files, "r")
            for line in searchfile:
#                if "GRD Lines" in line:
                if "INC Lines" in line:
                    Lines = [int(i) for i in line.split() if i.isdigit()][0]
#                    Lines = line[55:60]
                    if Lines not in Lines_list:
                        Lines_list.append(Lines)

                elif "INC Samples" in line:
#                elif "GRD Samples" in line:
                    Samples = [int(i) for i in line.split() if i.isdigit()][0]
#                    Samples = line[55:60]
                    if Samples not in Samples_list:
                        Samples_list.append(Samples)

#                elif "grd_mag.row_addr" in line:
                elif "inc.row_addr" in line:                     
                    Latitude = line.split()[3]
                    print(Latitude)
                    if Latitude not in Latitude_list:
                        Latitude_list.append(Latitude)

#                elif "grd_mag.col_addr" in line:
                elif "inc.col_addr" in line:
                    Longitude = line.split()[3]
                    print(Longitude)
                    if Longitude not in Longitude_list:
                        Longitude_list.append(Longitude)
            #Reset the variables to zero for each different flight date.
            var1 = 0
            searchfile.close()

    #var6 = 0

    # Step 3: Open HDR file and replace data.
    for files in os.listdir(folder):
        if files[-4:] == ".hdr":
            with open(files, "r") as sources:
                lines = sources.readlines()
            with open(files, "w") as sources:
                for line in lines:
                    if "DESCFIELD" in line:
                        sources.write(re.sub("DESCFIELD", "File Imported into ENVI.",line).lstrip())
#                        sources.write(re.sub(line[2:11], "", line))
                    elif "lines" in line:
                        sources.write(re.sub("NLINE", str(Lines_list[0]),line).lstrip())
#                        sources.write(re.sub(line[10:15], Lines_list[Files_list.index(files[0:18])], line))
                    elif "samples" in line:
                        sources.write(re.sub("NSAMP", str(Samples_list[0]),line).lstrip())
#                        sources.write(re.sub(line[10:15], Samples_list[Files_list.index(files[0:18])], line))
                    elif "LONGITUDE" in line:
                        sources.write(re.sub("LONGITUDE", str(Longitude_list[0]),line).lstrip())
                    
                    elif "LATITUDE" in line:
                        sources.write(re.sub("LATITUDE", str(Latitude_list[0]),line).lstrip())
                        
                    elif "LonSpace" in line:
                        sources.write(re.sub("LonSpace", str(LongitudeSpace_list[0]),line).lstrip())
                    
                    elif "LatSpace" in line:
                        sources.write(re.sub("LatSpace", str(LatitudeSpace_list[0]),line).lstrip())
                        
#                    elif "map info" in line:
#                        sources.write(re.sub(line[47:66], "{lon}, {lat}".format(
#                                                    lon=Longitude_list[Files_list.index(files[0:18])],
#                                                    lat=Latitude_list[Files_list.index(files[0:18])]), line))
                    else:
                        sources.write(line.lstrip())

    print("Finished creating hdrs")
    return    




##C:\Workstation\NC_Study\UAVSAR\Data\uavsar.asfdaac.alaska.edu
#workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\uavsar.asfdaac.alaska.edu\\'
#
#subfolder='UA_neuser_32023_18067_000_180920_L090_CX_01\\'
#
##

#


#C:\Workstation\NC_Study\UAVSAR\Data\
#workstation='C:\\Workstation\\NC_Study\\UAVSAR\\Data\\AlaskaMountains\\'

#subfolder='lclark_19205_19066_012_190917_L090_CX_01_grd\\'
#test=create_INC_header(workstation+subfolder)
#


