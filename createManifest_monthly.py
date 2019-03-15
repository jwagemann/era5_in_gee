#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 13:24:10 2019

@author: julia_wagemann
"""

from era5_in_gee_functions import createFileList, manifestToJSON, getEpochTimes_monthly, createManifest_monthly
import re


directory="/Volumes/FREECOM HDD/era5_tp/"
pattern="./tiff/monthly/2000/*.tif"
fileList=createFileList(directory,pattern)
print(fileList)

for file in fileList:
    tmp=re.findall("\d+",file)
    assetName=tmp[2]+tmp[3]+'_tp'
    print(assetName)
    ls_epochtimes = getEpochTimes_monthly(int(tmp[2]),int(tmp[3]))

    manifest = createManifest_monthly(eeCollectionName="projects/earthengine-legacy/assets/projects/ecmwf/era5_monthly/",
                          assetName=assetName,
                          parameter='tp',
                          bandIndex=0,
                          startTime=int(ls_epochtimes[0]),
                          endTime=int(ls_epochtimes[1]),
                          gs_bucket='gs://era5_tp_monthly/',
                          uris=file[20:],
                          year=int(tmp[2]),
                          month=int(tmp[3]))
    
    outfile='manifest_'+assetName+'_monthly'
    manifestToJSON(manifest,'/Volumes/FREECOM HDD/era5_tp/manifest/monthly/2000/',outfile)
