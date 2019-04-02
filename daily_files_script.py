#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:02:16 2019

@author: julia_wagemann
"""

import xarray as xr
from era5_in_gee_functions import createFileList, ncToTiff, createManifest_daily, getEpochTimes_daily, manifestToJSON, upload_blob
import time
import re
import os
from google.cloud import storage

execTime = time.time()

year='1983'
bucket_name = 'era5_tp_daily'
directory = '/Volumes/FREECOM HDD/era5_tp/'

# Create daily files
print("1st step - Create daily files")

fileList = createFileList(directory, './nc/'+year+'/era5_tp_'+year+'*')
fileList.sort()
print(fileList)

for file in fileList:
    array = xr.open_dataset(file, mask_and_scale=True, decode_times=True)
    outFileName = directory+'nc/daily/'+year+'/'+file[10:-3]+'_daily.nc'
    print(outFileName)
    array.resample(time='1D').sum().to_netcdf(outFileName, mode='w', compute=True)

#Convert daily files to tiffs
print("2nd step - Convert daily files to tiffs")
fileList = createFileList(directory, './nc/daily/'+year+'/era5_tp_'+year+'*')
fileList.sort()   
print(fileList) 

for file in fileList:
    print(file)
    tmp1 = re.findall("\d+", file)
    year = tmp1[2]
    outfile =  directory+'tiff/daily/'+year+'/'+file[16:-3]+'.tif'
    ncToTiff(file, 1,year,4326,outfile)

#Create manifest
print("3rd step - Create manifest of daily files")
fileList = createFileList(directory, './tiff/daily/'+year+'/*.tif')
fileList.sort()    
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
    directory_tiff = '/Volumes/FREECOM HDD/era5_tp/manifest/daily/'+year+'/'
    manifestToJSON(manifest,directory_tiff,outfile)

#Upload to GCP
print("4th step - Upload daily files to GCP")
fileList = createFileList(directory, './tiff/daily/'+year+'/*.tif')
fileList.sort()

for i in fileList:
    print(i)
    upload_blob(bucket_name, i, i[18:])

#Ingest to EE
print("5th step - Ingest to EE")
fileList = createFileList(directory, './manifest/daily/'+year+'/*.json')

for i in fileList:
    print(i)
    cmd = 'earthengine --use_cloud_api upload image --manifest ' + i
    os.system(cmd)

#Delete files from GCP
#print("6th step - Delete from GCP")
#storage_client = storage.Client()
#bucket = storage_client.get_bucket(bucket_name)
#blob_list = list(bucket.list_blobs(prefix="era5_tp_"))
#bucket.delete_blobs(blob_list)
#print('Files from GCP deleted')

print("The script took {0} second !".format(time.time() - execTime))