#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 22:09:23 2019

@author: julia_wagemann
"""

from era5_in_gee_functions import createFileList, manifestToJSON, getEpochTimes_daily, createManifest_daily
import re


directory="/Volumes/FREECOM HDD/era5_tp/"
pattern="./tiff/daily/2000/*.tif"
fileList=createFileList(directory,pattern)
print(fileList)

for file in fileList:
    tmp=re.findall("\d+",file)
    assetName=tmp[2]+tmp[3]+tmp[4]+'_tp'
    print(assetName)
    ls_epochtimes = getEpochTimes_daily(int(tmp[2]),int(tmp[3]),int(tmp[4]))

    manifest = createManifest_daily(eeCollectionName="projects/earthengine-legacy/assets/projects/ecmwf/era5_daily/",
                          assetName=assetName,
                          parameter='tp',
                          bandIndex=0,
                          startTime=int(ls_epochtimes[0]),
                          endTime=int(ls_epochtimes[1]),
                          gs_bucket='gs://era5_tp_daily/',
                          uris=file[18:],
                          year=int(tmp[2]),
                          month=int(tmp[3]),
                          day=int(tmp[4]))
    outfile='manifest_'+assetName+'_daily'
    manifestToJSON(manifest,'/Volumes/FREECOM HDD/era5_tp/manifest/daily/2000/',outfile)


