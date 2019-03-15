#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 11:57:02 2019

@author: julia_wagemann
"""

from era5_in_gee_functions import ncToTiff_hourly, createAssetName, createManifest, manifestToJSON, createFileList
import re
import time

###########################################
execTime = time.time()
fileList = createFileList('/Volumes/FREECOM HDD/era5_tp/','./nc/2000/era5_tp_2000*')
parameter='tp'
noOfBands=24

for i in fileList:
    print(i)
    tmp = i.split('_')
    tmp1 = re.findall("\d+", i)
    epoch_times = ncToTiff_hourly(i,parameter,noOfBands,4326,tmp[2])
    for j in range(0,len(epoch_times)-1):
        hour = str(j).zfill(2)
        assetName = createAssetName(i,parameter,hour)
        manifest = createManifest(eeCollectionName="projects/earthengine-legacy/assets/projects/ecmwf/era5_hourly/",
                                  assetName=assetName,
                                  parameter=parameter,
                                  bandIndex=j,
                                  startTime=epoch_times[j],
                                  endTime=epoch_times[j+1],
                                  gs_bucket="gs://era5_tp/",
                                  uris=i[10:-3]+'.tif',
                                  year=int(tmp1[2]),
                                  month=int(tmp1[3]),
                                  day=int(tmp1[4]),
                                  hour=int(hour))
        manifestToJSON(manifest,'./manifest/'+tmp1[2]+'/','manifest_'+assetName)
        
print("The script took {0} second !".format(time.time() - execTime))
