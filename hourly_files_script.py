#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Last updated: 19 December 2019

@author: julia_wagemann
"""

# Import libraries

from era5_in_gee_functions import uploadToGCP, convertFilesToTiff, createFileList, createListOfLists, createManifestCombined_hourly, ee_ingest
import time


###########################################

execTime = time.time()

yearList=['1982']
time_step='hourly'

directory1 = '/Volumes/G-DRIVE with Thunderbolt/'
directory2 = '/Volumes/jules_eh2/'
directory3 = '/Volumes/FREECOM HDD/'
directory4 = '/Volumes/LaCie/'

bucket = 'earthengine-ecmwf'
bucket_t2m = bucket+'/era5/era5_t2m'
bucket_tp = bucket+'/era5/era5_tp'
bucket_mx2t = bucket+'/era5/era5_mx2t'
bucket_mn2t = bucket+'/era5/era5_mn2t'
bucket_sp = bucket+'/era5/era5_sp'
bucket_mslp = bucket+'/era5/era5_msl'
bucket_2d = bucket+'/era5/era5_d2m'
bucket_u10 = bucket+'/era5/era5_u10'
bucket_v10 = bucket+'/era5/era5_v10'

directory_manifest = '/Volumes/G-DRIVE with Thunderbolt/manifests/'
directory_outfile = '/Volumes/G-DRIVE with Thunderbolt/manifests/era5_hourly/'

directory_list=[directory1+'era5_t2m/',
                directory1+'era5_minimum_2m_temperature_since_previous_post_processing',
                directory1+'era5_maximum_2m_temperature_since_previous_post_processing',
                directory2+'era5_2m_dewpoint_temperature',
                directory1+'era5_tp',
                directory4+'era5_surface_pressure',
                directory2+'era5_mean_sea_level_pressure',
                directory4+'era5_10m_u_component_of_wind',
                directory4+'era5_10m_v_component_of_wind']

print(directory_list)
bucket_list=[bucket_t2m, bucket_mn2t, bucket_mx2t, bucket_2d,bucket_tp, bucket_sp, bucket_mslp, bucket_u10, bucket_v10]

############################################

print('1st step - Convert hourly files to tiffs')

for year in yearList:
   # convertFilesToTiff(directory1, time_step, 't2m', year, 4326)
   # convertFilesToTiff(directory1, time_step, 'minimum_2m_temperature_since_previous_post_processing', year, 4326)
  #  convertFilesToTiff(directory1, time_step, 'maximum_2m_temperature_since_previous_post_processing', year, 4326)
    # convertFilesToTiff(directory3, time_step, 'tp', year, 4326)
    # convertFilesToTiff(directory2, time_step, '2m_dewpoint_temperature', year, 4326)
    # convertFilesToTiff(directory2, time_step, 'mean_sea_level_pressure', year, 4326)
    # convertFilesToTiff(directory4, time_step, 'surface_pressure', year, 4326)
    # convertFilesToTiff(directory4, time_step, '10m_u_component_of_wind', year, 4326)

    # convertFilesToTiff(directory4, time_step, '10m_v_component_of_wind', year, 4326)


    print("2nd step - Upload files to GCP")
   # uploadToGCP(directory1,year,time_step,'t2m',bucket)
  #  uploadToGCP(directory1,year,time_step,'minimum_2m_temperature_since_previous_post_processing',bucket)
#    uploadToGCP(directory1,year,time_step,'maximum_2m_temperature_since_previous_post_processing',bucket)
 #   uploadToGCP(directory1,year,time_step,'tp',bucket)
  #  uploadToGCP(directory2,year,time_step,'2m_dewpoint_temperature',bucket)
 #   uploadToGCP(directory4,year,time_step,'surface_pressure',bucket)
   # uploadToGCP(directory2,year,time_step,'mean_sea_level_pressure',bucket)
 #   uploadToGCP(directory4,year,time_step,'10m_u_component_of_wind',bucket)
#    uploadToGCP(directory4,year,time_step,'10m_v_component_of_wind',bucket)



    # print("3rd step - Create manifests")

    # fileList=createListOfLists(directory_list,'hourly',year)
    # print(fileList)
    # ncFileList = createFileList(directory1,'./era5_t2m/nc/hourly/'+year+'/*')
    # print(len(ncFileList))

    # createManifestCombined_hourly(fileList, ncFileList, year, bucket_list, directory_manifest,directory_outfile)


    print('4th step - Ingest to EE')
    month_list=['01','02','03']
    for i in month_list:
        manifest_list = createFileList(directory_outfile+year+'/', 'manifest_'+year+i+'*')
        print(manifest_list)
        ee_ingest(manifest_list)



print("The script took {0} second !".format(time.time() - execTime))