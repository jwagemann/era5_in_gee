#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 15:46:02 2019

@author: julia_wagemann
"""

import xarray as xr
from era5_in_gee_functions import createFileList, manifestToJSON, upload_blob, ncToTiff, getEpochTimes_monthly, updateManifest_monthly, createMonthlyFiles, convertMonthlyFilesToTiff, uploadMonthlyFilesToGCP, createDailyFiles
import time
import os
import re
import glob
from google.cloud import storage

execTime = time.time()
#directory1 = '/Volumes/jules_eh/era5_t2m/'
#directory2 = '/Volumes/FREECOM HDD/era5_tp/'

directory1 = '/Volumes/jules_eh/'
directory2 = '/Volumes/jules_eh2/'
directory3 = '/Volumes/FREECOM HDD/'

yearList=['2010','2011','2012','2013','2014','2015','2016','2017']
year='2018'

bucket_t2m = 'era5_t2m_monthly'
bucket_tp = 'era5_tp_monthly'
bucket_mx2t = 'era5_mx2t_monthly'
bucket_mn2t = 'era5_mn2t_monthly'


createDailyFiles(directory1,'t2m',year,'mean')
createDailyFiles(directory1,'t2m',year,'min')
createDailyFiles(directory1,'t2m',year,'max')
#createDailyFiles(directory1, 'minimum_2m_temperature_since_previous_post_processing', year,'min')
#createDailyFiles(directory1, 'maximum_2m_temperature_since_previous_post_processing', year,'max')

#
###############
#print('1st step - Create monthly files')
#    
#    createMonthlyFiles(directory1, 't2m', year, 'mean')
#    createMonthlyFiles(directory3, 'tp', year, 'sum')
#    createMonthlyFiles(directory1, 'minimum_2m_temperature_since_previous_post_processing', year, 'min')
#    createMonthlyFiles(directory1, 'maximum_2m_temperature_since_previous_post_processing', year, 'max')

##    month_list = ['01','02','03','04','05','06','07','08','09','10','11','12']
#
#    for i in month_list:
#        fileList
#        
#        
#        fileList_t2m = createFileList(directory1,'./nc/'+year+'/era5_t2m_'+year+'_'+i+'*')
#        fileList_tp = createFileList(directory2,'./nc/'+year+'/era5_tp_'+year+'_'+i+'*')
#        fileList_t2m.sort()
#        fileList_tp.sort()
#        print(fileList_t2m)
#        print(fileList_tp)
#        os.chdir(directory1)
#        array_t2m = xr.open_mfdataset(fileList_t2m)
#        outFileName_t2m = directory1+'nc/monthly/'+year+'/era5_'+param1+'_'+year+'_'+i+'.nc'
#        array_t2m.resample(time='1M').mean().to_netcdf(outFileName_t2m, mode='w', compute=True)
#        
#        os.chdir(directory2)
#        array_tp = xr.open_mfdataset(fileList_tp)
#        outFileName_tp = directory2+'nc/monthly/'+year+'/era5_'+param2+'_'+year+'_'+i+'.nc'
#        array_tp.resample(time='1M').sum().to_netcdf(outFileName_tp, mode='w', compute=True)        
#    
    
    ##################

#    print('2nd step - Convert monthly files to tiffs')
#    
#    convertMonthlyFilesToTiff(directory1,'t2m',year,4326)
#    convertMonthlyFilesToTiff(directory3,'tp',year,4326)
#    convertMonthlyFilesToTiff(directory1,'minimum_2m_temperature_since_previous_post_processing',4326)
#    convertMonthlyFilesToTiff(directory1,'maximum_2m_temperature_since_previous_post_processing',4326)
#    

#    fileList_t2m = createFileList(directory1,'./nc/monthly/'+year+'/*.nc')
#    fileList_tp = createFileList(directory2,'./nc/monthly/'+year+'/*.nc')
#    fileList_t2m.sort()
#    fileList_tp.sort()
#    print(fileList_t2m)
#    print(fileList_tp)
#    
#    for file1,file2 in zip(fileList_t2m,fileList_tp):
#        print(file1, file2)
#        tmp1 = re.findall("\d+", file1)
#        year = tmp1[3]
#        outfile1 = directory1+'tiff/monthly/'+year+'/'+file1[18:-3]+'.tif'
#        outfile2 = directory2+'tiff/monthly/'+year+'/'+file2[18:-3]+'.tif'
#        print(outfile1)
#        print(outfile2)
#        os.chdir(directory1)
#        ncToTiff(file1,1,year,4326, outfile1)
#        os.chdir(directory2)
#        ncToTiff(file2,1,year,4326, outfile2)
#    
#    ####################
#    
#    print('3rd step - Create manifests')
#    
#    fileList1=createFileList(directory1,"./tiff/monthly/"+year+"/*.tif")
#    fileList2=createFileList(directory2,"./tiff/monthly/"+year+"/*.tif")
#    param1 = 't2m'
#    param2 = 'tp'
#    print(fileList1)
#    print(fileList2)
#    fileList1.sort()
#    fileList2.sort()
#    
#    for file1,file2 in zip(fileList1,fileList2):
#        print(file1)
#        tmp=re.findall("\d+",file1)
#        print(tmp)
#        assetName=tmp[3]+tmp[4]
#        ls_epochtimes = getEpochTimes_monthly(int(tmp[3]),int(tmp[4]))
#        year=tmp[3]
#        month=tmp[4]
#        print(assetName)
#    
#    
#        manifest = updateManifest_monthly(directory1, eeCollectionName="projects/earthengine-legacy/assets/projects/ecmwf/era5_monthly/",
#                              assetName=assetName,
#                              startTime=int(ls_epochtimes[0]),
#                              endTime=int(ls_epochtimes[1]),
#                              gs_bucket1='gs://'+bucket_t2m+'/',
#                              gs_bucket2='gs://'+bucket_tp+'/',
#                              uris1=file1[20:],
#                              uris2=file2[20:],
#                              year=int(year),
#                              month=int(month))
#    
#        print(manifest)
#        outfile='manifest_'+assetName+'_monthly'
#        print(outfile)
#        manifestToJSON(manifest,directory1+'manifest/monthly/'+year+'/',outfile)
#    
#    #####################
#    
    #Upload to GCP
#    print("4th step - Upload monthly files to GCP")
#    
#    uploadMonthlyFilesToGCP(directory1,'t2m',year,bucket_t2m)
#    uploadMonthlyFilesToGCP(directory3,'tp',year,bucket_tp)
#    uploadMonthlyFilesToGCP(directory1, 'minimum_2m_temperature_since_previous_post_processing', year, bucket_mn2t)
#    uploadMonthlyFilesToGCP(directory1, 'maximum_2m_temperature_since_previous_post_processig', year, bucket_mx2t)
##    fileList1 = createFileList(directory1, './tiff/monthly/'+year+'/*.tif')
#    fileList2 = createFileList(directory2, './tiff/monthly/'+year+'/*.tif')
#    fileList1.sort()
#    fileList2.sort()
#    
#    for i,j in zip(fileList1,fileList2):
#        print(i,j)
#        os.chdir(directory1)
#        upload_blob(bucket_t2m, i, i[20:])
#        os.chdir(directory2)
#        upload_blob(bucket_tp,j,j[20:])
#    
#    #Ingest to EE
#    print("5th step - Ingest to EE")
#    fileList = createFileList(directory1, './manifest/monthly/'+year+'/*.json')
#    print(fileList)
#    
#    for i in fileList:
#        print(i)
#        cmd = 'earthengine --use_cloud_api upload image --manifest ' + i
#        os.system(cmd)

##Delete files from GCP
#print("6th step - Delete from GCP")
#storage_client = storage.Client()
#bucket = storage_client.get_bucket(bucket_name)
#blob_list = list(bucket.list_blobs(prefix="era5_"+parameter+"_"+year))
#print(blob_list)
#bucket.delete_blobs(blob_list)
#print('Files from GCP deleted')
#
print("The script took {0} second !".format(time.time() - execTime))