#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:02:16 2019

@author: julia_wagemann
"""

import xarray as xr
from era5_in_gee_functions import createFileList, ncToTiff, updateManifest_daily, getEpochTimes_daily, manifestToJSON, upload_blob
import time
import re
import os
from google.cloud import storage


execTime = time.time()
#directory1 = '/Volumes/jules_eh/era5_t2m/'
#directory2 = '/Volumes/FREECOM HDD/era5_tp/'
#yearList=['2006']
bucket_t2m = 'era5_t2m_daily'
bucket_tp = 'era5_tp_daily'
#param1 = 't2m'
#param2 = 'tp'
#
#for year in yearList:
#    print(year)
#    # Create daily files
#    print("1st step - Create daily files")
#    
#    fileList_tp = createFileList(directory2, './nc/'+year+'/era5_'+param2+'_'+year+'*')
#    fileList_t2m = createFileList(directory1, './nc/'+year+'/era5_'+param1+'_'+year+'*')
#    fileList_tp.sort()
#    fileList_t2m.sort()
#    print(fileList_tp)
#    print(fileList_t2m)
#    
#    for file1,file2 in zip(fileList_t2m, fileList_tp):
#        os.chdir(directory1)
#        array_t2m = xr.open_dataset(file1, mask_and_scale=True, decode_times=True)
#        os.chdir(directory2)
#        array_tp = xr.open_dataset(file2, mask_and_scale=True, decode_times=True)
#        
#        outFileName_t2m = directory1+'nc/daily/'+year+'/'+file1[10:-3]+'_daily.nc'
#        outFileName_tp = directory2+'nc/daily/'+year+'/'+file2[10:-3]+'_daily.nc'
#        
#        print(outFileName_t2m)
#        print(outFileName_tp)
#        
#        array_t2m.resample(time='1D').mean().to_netcdf(outFileName_t2m, mode='w', compute=True)
#        array_tp.resample(time='1D').sum().to_netcdf(outFileName_tp, mode='w', compute=True)
#        
#    
#    #Convert daily files to tiffs
#    print("2nd step - Convert daily files to tiffs")
#    os.chdir(directory1)
#    fileList_t2m = createFileList(directory1, './nc/daily/'+year+'/era5_t2m_'+year+'*')
#    os.chdir(directory2)
#    fileList_tp = createFileList(directory2, './nc/daily/'+year+'/era5_tp_'+year+'*')
#    
#    fileList_t2m.sort() 
#    fileList_tp.sort()  
#    print(fileList_t2m) 
#    print(fileList_tp)
#    
#    for file1, file2 in zip(fileList_t2m,fileList_tp):
#        print(file1, file2)
#        tmp1 = re.findall("\d+", file1)
#        print(tmp1)
#        year = tmp1[0]
#        outfile_t2m =  directory1+'tiff/daily/'+year+'/'+file1[16:-3]+'.tif'
#        outfile_tp =  directory2+'tiff/daily/'+year+'/'+file2[16:-3]+'.tif'
#        os.chdir(directory1)
#        ncToTiff(file1, 1,year,4326,outfile_t2m)
#        os.chdir(directory2)
#        ncToTiff(file2, 1,year,4326,outfile_tp)
#    
#    #Create manifest
#    print("3rd step - Create manifest of daily files")
#    fileList_t2m = createFileList(directory1, './tiff/daily/'+year+'/*.tif')
#    fileList_tp = createFileList(directory2, './tiff/daily/'+year+'/*.tif')
#    
#    fileList_t2m.sort()  
#    fileList_tp.sort()  
#    
#    print(fileList_t2m)
#    print(fileList_tp)
#    
#    for file1,file2 in zip(fileList_t2m,fileList_tp):
#        tmp=re.findall("\d+",file1)
#        print(tmp)
#        assetName=tmp[3]+tmp[4]+tmp[5]
#        print(assetName)
#        ls_epochtimes = getEpochTimes_daily(int(tmp[3]),int(tmp[4]),int(tmp[5]))
#    
#        manifest = updateManifest_daily(directory1, eeCollectionName="projects/earthengine-legacy/assets/projects/ecmwf/era5_daily/",
#                              assetName=assetName,
#                              startTime=int(ls_epochtimes[0]),
#                              endTime=int(ls_epochtimes[1]),
#                              gs_bucket1='gs://'+bucket_t2m+'/',
#                              gs_bucket2='gs://'+bucket_tp+'/',
#                              uris1=file1[18:],
#                              uris2=file2[18:],
#                              year=int(tmp[3]),
#                              month=int(tmp[4]),
#                              day=int(tmp[5]))
#        print(manifest)
#        outfile='manifest_'+assetName+'_daily'
#        manifestToJSON(manifest,directory1+'manifest/daily/'+year+'/',outfile)
#    
#    #Upload to GCP
#    print("4th step - Upload daily files to GCP")
#    fileList_t2m = createFileList(directory1, './tiff/daily/'+year+'/*.tif')
#    fileList_tp = createFileList(directory2, './tiff/daily/'+year+'/*.tif')
#    
#    fileList_t2m.sort()
#    fileList_tp.sort()
#    
#    for i,j in zip(fileList_t2m, fileList_tp):
#        print(i,j)
#        os.chdir(directory1)
#        upload_blob(bucket_t2m, i, i[18:])
#        os.chdir(directory2)
#        upload_blob(bucket_tp, j, j[18:])
#    
#    #Ingest to EE
#    print("5th step - Ingest to EE")
#    fileList = createFileList(directory1, './manifest/daily/'+year+'/*.json')
#    
#    for i in fileList:
#        print(i)
#        cmd = 'earthengine --use_cloud_api upload image --manifest ' + i
#        os.system(cmd)
    
    #Delete files from GCP
print("6th step - Delete from GCP")
storage_client = storage.Client()
bucket = storage_client.get_bucket(bucket_t2m)
blob_list = list(bucket.list_blobs(prefix="era5_t2m_"))
bucket.delete_blobs(blob_list)
print('Files from GCP deleted')
    
print("The script took {0} second !".format(time.time() - execTime))