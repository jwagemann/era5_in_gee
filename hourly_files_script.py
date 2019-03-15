#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 16:36:01 2019

@author: julia_wagemann
"""

from era5_in_gee_functions import ncToTiff_hourly, createAssetName, createManifest, manifestToJSON, createFileList, upload_blob
import re
import time
from google.cloud import storage
import os

###########################################
execTime = time.time()
directory='/Volumes/FREECOM HDD/era5_tp/'
bucket_name='era5_tp'
year='2000'

############################################
#print('1st step - Convert hourly files to tiffs and create manifests')
#fileList = createFileList(directory,'./nc/2000/era5_tp_'+year+'*')
#parameter='tp'
#noOfBands=24
#
#for i in fileList:
#    print(i)
#    tmp = i.split('_')
#    tmp1 = re.findall("\d+", i)
#    epoch_times = ncToTiff_hourly(i,parameter,noOfBands,4326,tmp[2])
#    for j in range(0,len(epoch_times)-1):
#        hour = str(j).zfill(2)
#        assetName = createAssetName(i,parameter,hour)
#        manifest = createManifest(eeCollectionName="projects/earthengine-legacy/assets/projects/ecmwf/era5_hourly/",
#                                  assetName=assetName,
#                                  parameter=parameter,
#                                  bandIndex=j,
#                                  startTime=epoch_times[j],
#                                  endTime=epoch_times[j+1],
#                                  gs_bucket="gs://"+bucket_name,
#                                  uris=i[10:-3]+'.tif',
#                                  year=int(tmp1[2]),
#                                  month=int(tmp1[3]),
#                                  day=int(tmp1[4]),
#                                  hour=int(hour))
#        manifestToJSON(manifest,'./manifest/'+tmp1[2]+'/','manifest_'+assetName)
        

##Upload to GCP
#print("2nd step - Upload daily files to GCP")
#fileList = createFileList(directory, './tiff/'+year+'/*.tif')
#fileList.sort()
#
#for i in fileList:
#    print(i)
#    upload_blob(bucket_name, i, i[13:])

#Ingest to EE
print("3rd step - Ingest to EE")
fileList = createFileList(directory, './manifest/'+year+'/*.json')
print(len(fileList))

for i in fileList[3346:]:
    print(i)
    cmd = 'earthengine --use_cloud_api upload image --manifest ' + i
    os.system(cmd)

##Delete files from GCP
#print("6th step - Delete from GCP")
#storage_client = storage.Client()
#bucket = storage_client.get_bucket(bucket_name)
#blob_list = list(bucket.list_blobs(prefix="era5_tp_"+year))
#bucket.delete_blobs(blob_list)
#print('Files from GCP deleted')

print("The script took {0} second !".format(time.time() - execTime))