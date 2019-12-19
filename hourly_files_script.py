#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 16:36:01 2019

@author: julia_wagemann
"""

from era5_in_gee_functions import ncToTiff_hourly, uploadToGCP, convertFilesToTiff, createFileList
import re
import time
from google.cloud import storage
import os

###########################################
#execTime = time.time()
#directory='/Volumes/FREECOM HDD/era5_tp/'
#bucket_name='era5_tp'
#year='2000'

execTime = time.time()

yearList = ['2019']
directory1 = '/Volumes/G-DRIVE with Thunderbolt/'
directory2 = '/Volumes/jules_eh2/'
directory3 = '/Volumes/FREECOM HDD/'
directory4 = '/Volumes/LaCie/'

bucket_t2m = 'era5_t2m'
bucket_tp = 'era5_tp'
bucket_mx2t = 'era5_mx2t'
bucket_mn2t = 'era5_mn2t'
bucket_sp = 'era5_sp'
bucket_mslp = 'era5_mslp'
bucket_2d = 'era5_2d'
bucket_u10 = 'era5_u10'
bucket_v10 = 'era5_v10'

directory_manifest = '/Volumes/jules_eh3/manifests/'
directory_outfile = '/Volumes/jules_eh3/manifests/era5_hourly/'

############################################
print('1st step - Convert hourly files to tiffsc')

yearList=['1980']

time_step='hourly'
noOfBands=24

for year in yearList:
    convertFilesToTiff(directory1, time_step, 't2m', year, 4326)
    convertFilesToTiff(directory1, time_step, 'minimum_2m_temperature_since_previous_post_processing', year, 4326)
    convertFilesToTiff(directory1, time_step, 'maximum_2m_temperature_since_previous_post_processing', year, 4326)
    convertFilesToTiff(directory3, time_step, 'tp', year, 4326)
    convertFilesToTiff(directory2, time_step, '2m_dewpoint_temperature', year, 4326)
    convertFilesToTiff(directory2, time_step, 'mean_sea_level_pressure', year, 4326)
    convertFilesToTiff(directory4, time_step, 'surface_pressure', year, 4326)
    convertFilesToTiff(directory4, time_step, '10m_u_component_of_wind', year, 4326)
    convertFilesToTiff(directory4, time_step, '10m_v_component_of_wind', year, 4326)



    uploadToGCP(directory1,year,time_step,'t2m',bucket_t2m)
    uploadToGCP(directory1,year,time_step,'minimum_2m_temperature_since_previous_post_processing',bucket_mn2t)
    uploadToGCP(directory1,year,time_step,'maximum_2m_temperature_since_previous_post_processing',bucket_mx2t)
    uploadToGCP(directory3,year,time_step,'tp',bucket_tp)
    uploadToGCP(directory2,year,time_step,'2m_dewpoint_temperature',bucket_2d)
    uploadToGCP(directory4,year,time_step,'surface_pressure',bucket_sp)
    uploadToGCP(directory2,year,time_step,'mean_sea_level_pressure',bucket_mslp)
    uploadToGCP(directory4,year,time_step,'10m_u_component_of_wind',bucket_u10)
    uploadToGCP(directory4,year,time_step,'10m_v_component_of_wind',bucket_v10)




# directory_list=[directory1+'era5_t2m',
# #                directory1+'era5_minimum_2m_temperature_since_previous_post_processing',
# #                directory1+'era5_maximum_2m_temperature_since_previous_post_processing',
#                 directory2+'era5_2m_dewpoint_temperature',
#                 directory2+'era5_surface_pressure',
#                 directory2+'era5_mean_sea_level_pressure',
#                 directory2+'era5_10m_u_component_of_wind',
#                 directory2+'era5_10m_v_component_of_wind']
# print(directory_list)
# bucket_list=[bucket_t2m, bucket_2d, bucket_sp, bucket_mslp, bucket_u10, bucket_v10]
#     #
# fileList=createListOfLists(directory_list,time_step,year)

# updateManifest_hourly(directory, eeCollectionName, assetName, startTime, endTime, bandIndex, gs_bucket_list, uris1, uris2, uris3, uris4, uris5, uris6, uris7, uris8, year,month, day, hour)
    
# createManifestCombined_hourly(fileList, year, bucket_list, directory_manifest,directory_outfile)
    #
#    createManifestCombined_hourly(fileList, year, bucket_list, directory_manifest,directory_outfile)


#for i in fileList:
#    print(i)
#    tmp = i.split('_')
#    print(tmp)
#    tmp1 = re.findall("\d+", i)
#    print(tmp1)

#    epoch_times = ncToTiff_hourly(i,parameter,noOfBands,4326,tmp[2])
#    print(epoch_times)
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
#        

##Upload to GCP
#print("2nd step - Upload daily files to GCP")
#fileList = createFileList(directory, './tiff/'+year+'/*.tif')
#fileList.sort()
#
#for i in fileList:
#    print(i)
#    upload_blob(bucket_name, i, i[13:])

#Ingest to EE
#print("3rd step - Ingest to EE")
#fileList = createFileList(directory, './manifest/'+year+'/*.json')
#print(len(fileList))
#
#for i in fileList[3346:]:
#    print(i)
#    cmd = 'earthengine --use_cloud_api upload image --manifest ' + i
#    os.system(cmd)

##Delete files from GCP
#print("6th step - Delete from GCP")
#storage_client = storage.Client()
#bucket = storage_client.get_bucket(bucket_name)
#blob_list = list(bucket.list_blobs(prefix="era5_tp_"+year))
#bucket.delete_blobs(blob_list)
#print('Files from GCP deleted')

print("The script took {0} second !".format(time.time() - execTime))