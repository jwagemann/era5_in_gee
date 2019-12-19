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

yearList=['1980']
time_step='hourly'

directory1 = '/Volumes/G-DRIVE with Thunderbolt/'
directory2 = '/Volumes/jules_eh2/'
directory3 = '/Volumes/FREECOM HDD/'
directory4 = '/Volumes/LaCie/'

bucket_t2m = 'era5_t2m_daily'
bucket_tp = 'era5_tp_daily'
bucket_mx2t = 'era5_mx2t_daily'
bucket_mn2t = 'era5_mn2t_daily'
bucket_sp = 'era5_sp_daily'
bucket_mslp = 'era5_mslp_daily'
bucket_2d = 'era5_2d_daily'
bucket_u10 = 'era5_u10_daily'
bucket_v10 = 'era5_v10_daily'

directory_manifest = '/Volumes/jules_eh3/manifests/'
directory_outfile = '/Volumes/jules_eh3/manifests/era5_hourly/'

directory_list=[directory1+'/era5_t2m/',
                directory1+'/era5_minimum_2m_temperature_since_previous_post_processing',
                directory1+'/era5_maximum_2m_temperature_since_previous_post_processing',
                directory2+'/era5_2m_dewpoint_temperature',
                directory3+'/era5_tp',
                directory4+'/era5_surface_pressure',
                directory2+'/era5_mean_sea_level_pressure',
                directory4+'/era5_10m_u_component_of_wind',
                directory4+'/era5_10m_v_component_of_wind']

print(directory_list)
bucket_list=[bucket_t2m, bucket_mn2t, bucket_mx2t, bucket_2d,bucket_tp, bucket_sp, bucket_mslp, bucket_u10, bucket_v10]

############################################

print('1st step - Convert hourly files to tiffs')

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


    print("2nd step - Upload files to GCP")
    uploadToGCP(directory1,year,time_step,'t2m',bucket_t2m)
    uploadToGCP(directory1,year,time_step,'minimum_2m_temperature_since_previous_post_processing',bucket_mn2t)
    uploadToGCP(directory1,year,time_step,'maximum_2m_temperature_since_previous_post_processing',bucket_mx2t)
    uploadToGCP(directory3,year,time_step,'tp',bucket_tp)
    uploadToGCP(directory2,year,time_step,'2m_dewpoint_temperature',bucket_2d)
    uploadToGCP(directory4,year,time_step,'surface_pressure',bucket_sp)
    uploadToGCP(directory2,year,time_step,'mean_sea_level_pressure',bucket_mslp)
    uploadToGCP(directory4,year,time_step,'10m_u_component_of_wind',bucket_u10)
    uploadToGCP(directory4,year,time_step,'10m_v_component_of_wind',bucket_v10)



    print("3rd step - Create manifests")

    fileList=createListOfLists(directory_list,'hourly',year)
    print(len(fileList))
    ncFileList = createFileList(directory1,'./era5_t2m/nc/hourly/'+year+'/*')
    print(len(ncFileList))

    createManifestCombined_hourly(fileList, ncFileList, year, bucket_list, directory_manifest,directory_outfile)


    print('4th step - Ingest to EE')

    manifest_list = createFileList(directory_outfile+year+'/', '*.json')
    print(manifest_list)
    ee_ingest(manifest_list)



print("The script took {0} second !".format(time.time() - execTime))