#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 15:46:02 2019

@author: julia_wagemann
"""

from era5_in_gee_functions import createFileList, createListOfLists, createMonthlyFiles, convertMonthlyFilesToTiff, uploadMonthlyFilesToGCP, createManifestCombined_monthly, ee_ingest
import time



execTime = time.time()

############################################

directory1 = '/Volumes/G-Drive with Thunderbolt/'
directory2 = '/Volumes/jules_eh2/'
directory3 = '/Volumes/FREECOM HDD/'
directory4 = '/Volumes/LaCie/'

yearList=['2010','2011','2012','2013','2014','2015','2016','2017']

bucket_t2m = 'era5_t2m_monthly'
bucket_tp = 'era5_tp_monthly'
bucket_mx2t = 'era5_mx2t_monthly'
bucket_mn2t = 'era5_mn2t_monthly'
bucket_sp = 'era5_sp_monthly'
bucket_mslp = 'era5_mslp_monthly'
bucket_2d = 'era5_2d_monthly'
bucket_u10 = 'era5_u10_monthly'
bucket_v10 = 'era5_v10_monthly'

directory_manifest = '/Volumes/G-Drive with Thunderbolt/manifests/'
directory_outfile = '/Volumes/G-Drive with Thunderbolt/manifests/era5_monthly/'

############################################

for year in yearList:

    print('1st step - Create monthly files')

    createMonthlyFiles(directory1, 't2m', year, 'mean')
    createMonthlyFiles(directory3, 'tp', year, 'sum')
    createMonthlyFiles(directory1, 'minimum_2m_temperature_since_previous_post_processing', year, 'min')
    createMonthlyFiles(directory1, 'maximum_2m_temperature_since_previous_post_processing', year, 'max')
    createMonthlyFiles(directory2, '2m_dewpoint_temperature',year,'mean')
    createMonthlyFiles(directory2, 'mean_sea_level_pressure',year,'mean')
    createMonthlyFiles(directory4, 'surface_pressure',year,'mean')
    createMonthlyFiles(directory4, '10m_u_component_of_wind',year,'mean')
    createMonthlyFiles(directory4, '10m_v_component_of_wind',year,'mean')


    print('2nd step - Convert monthly files to tiffs')

    convertMonthlyFilesToTiff(directory1,'t2m',year,4326)
    convertMonthlyFilesToTiff(directory3,'tp',year,4326)
    convertMonthlyFilesToTiff(directory1,'minimum_2m_temperature_since_previous_post_processing',4326)
    convertMonthlyFilesToTiff(directory1,'maximum_2m_temperature_since_previous_post_processing',4326)
    convertMonthlyFilesToTiff(directory2, 'daily', 'mean_sea_level_pressure', year, 4326)
    convertMonthlyFilesToTiff(directory4, 'daily', 'surface_pressure', year, 4326)
    convertMonthlyFilesToTiff(directory4, 'daily', '10m_u_component_of_wind', year, 4326)
    convertMonthlyFilesToTiff(directory4, 'daily', '10m_v_component_of_wind', year, 4326)



    print("3rd step - Upload monthly files to GCP")

    uploadMonthlyFilesToGCP(directory1,'t2m',year,bucket_t2m)
    uploadMonthlyFilesToGCP(directory3,'tp',year,bucket_tp)
    uploadMonthlyFilesToGCP(directory1, 'minimum_2m_temperature_since_previous_post_processing', year, bucket_mn2t)
    uploadMonthlyFilesToGCP(directory1, 'maximum_2m_temperature_since_previous_post_processig', year, bucket_mx2t)

    uploadMonthlyFilesToGCP(directory2,'2m_dewpoint_temperature',year,bucket_2d)
    uploadMonthlyFilesToGCP(directory4,'surface_pressure',year,bucket_sp)
    uploadMonthlyFilesToGCP(directory2,'mean_sea_level_pressure',year,bucket_mslp)
    uploadMonthlyFilesToGCP(directory4,'10m_u_component_of_wind',year,bucket_u10)
    uploadMonthlyFilesToGCP(directory4,'10m_v_component_of_wind',year,bucket_v10)


    print('4th step - Create manifests')

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
    bucket_list=[bucket_t2m, bucket_mn2t, bucket_mx2t, bucket_2d, bucket_tp, bucket_sp, bucket_mslp, bucket_u10, bucket_v10]

    fileList=createListOfLists(directory_list,'monthly',year)

    createManifestCombined_monthly(fileList, year,bucket_list, directory_manifest,directory_outfile)


    #Ingest to EE
    print("5th step - Ingest to EE")

    manifest_list = createFileList(directory_outfile+year+'/', '*.json')
    print(year)
    print(len(manifest_list))
    if(len(manifest_list)<365 and year!='1979'):
        break
    else:
        ee_ingest(manifest_list)


print("The script took {0} second !".format(time.time() - execTime))