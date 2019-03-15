#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 15:46:02 2019

@author: julia_wagemann
"""

import xarray as xr
from era5_in_gee_functions import createFileList, createManifest_monthly, manifestToJSON, upload_blob, ncToTiff, getEpochTimes_monthly
import time
import os
import re
from google.cloud import storage

execTime = time.time()
directory = '/Volumes/FREECOM HDD/era5_tp/'
year='2018'
bucket_name = 'era5_tp_monthly'

################
#print('1st step - Create monthly files')
#month_list = ['01','02','03','04','05','06','07','08','09','10']
#for i in month_list:
#    fileList = createFileList(directory,'./nc/'+year+'/era5_tp_'+year+'_'+i+'*')
#    fileList.sort()
#    print(fileList)
#
#    array = xr.open_mfdataset(fileList)
#    outFileName = directory+'nc/monthly/'+year+'/era5_tp_'+year+'_'+i+'.nc'
#    array.resample(time='1M').sum().to_netcdf(outFileName, mode='w', compute=True)

####################
    
print('2nd step - Convert monthly files to tiff')
fileList = createFileList(directory,'./nc/monthly/'+year+'/*.nc')
fileList.sort()
print(fileList)

for file in fileList:
    print(file)
    tmp1 = re.findall("\d+", file)
    year = tmp1[2]
    outfile = directory+'tiff/monthly/'+year+'/'+file[18:-3]+'.tif'
    ncToTiff(file, 1,year,4326, outfile)

#####################

print('3rd step - Create manifests')

fileList=createFileList(directory,"./tiff/monthly/"+year+"/*.tif")
print(fileList)
fileList.sort()

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
                          gs_bucket='gs://'+bucket_name+'/',
                          uris=file[20:],
                          year=int(tmp[2]),
                          month=int(tmp[3]))
    
    outfile='manifest_'+assetName+'_monthly'
    manifestToJSON(manifest,directory+'manifest/monthly/'+year+'/',outfile)

######################

#Upload to GCP
print("4th step - Upload monthly files to GCP")
fileList = createFileList(directory, './tiff/monthly/'+year+'/*.tif')
fileList.sort()

for i in fileList:
    print(i)
    upload_blob(bucket_name, i, i[20:])

#Ingest to EE
print("5th step - Ingest to EE")
fileList = createFileList(directory, './manifest/monthly/'+year+'/*.json')
print(fileList)

for i in fileList:
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