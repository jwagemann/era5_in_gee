#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:02:16 2019

@author: julia_wagemann
"""


from era5_in_gee_functions import createFileList, createDailyFiles, convertFilesToTiff, uploadToGCP, createManifestCombined_daily, createListOfLists, ee_ingest
import time

import os

###########################################

execTime = time.time()

directory1 = '/Volumes/G-Drive with Thunderbolt/'
directory2 = '/Volumes/jules_eh2/'
directory3 = '/Volumes/FREECOM HDD/'
directory4 = '/Volumes/LaCie/'


#yearList = ['1990','1991','1992','1993','1994','1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019']
yearList = ['1988','1989','1990']


bucket_t2m = 'era5_t2m_daily'
bucket_tp = 'era5_tp_daily'
bucket_mx2t = 'era5_mx2t_daily'
bucket_mn2t = 'era5_mn2t_daily'
bucket_sp = 'era5_sp_daily'
bucket_mslp = 'era5_mslp_daily'
bucket_2d = 'era5_2d_daily'
bucket_u10 = 'era5_u10_daily'
bucket_v10 = 'era5_v10_daily'

directory_manifest = '/Volumes/G-Drive with Thunderbolt/manifests/'
directory_outfile = '/Volumes/G-Drive with Thunderbolt/manifests/era5_daily/'

############################################

for year in yearList:

    print("1st step - Resample hourly information to daily aggregates")
    createDailyFiles(directory1,'t2m',year,'mean')
    createDailyFiles(directory1,'t2m',year,'min')
    createDailyFiles(directory1,'t2m',year,'max')
    createDailyFiles(directory3, 'tp',year,'sum')
    createDailyFiles(directory2, '2m_dewpoint_temperature',year,'mean')
    createDailyFiles(directory2, 'mean_sea_level_pressure',year,'mean')
    createDailyFiles(directory4, 'surface_pressure',year,'mean')
    createDailyFiles(directory4, '10m_u_component_of_wind',year,'mean')
    createDailyFiles(directory4, '10m_v_component_of_wind',year,'mean')

#    #Convert daily files to tiffs
    print("2nd step - Convert daily files to tiffs")
    convertFilesToTiff(directory1, 'daily', 't2m', year, 4326)
    convertFilesToTiff(directory3, 'daily', 'tp', year, 4326)
    convertFilesToTiff(directory2, 'daily', '2m_dewpoint_temperature', year, 4326)
    convertFilesToTiff(directory2, 'daily', 'mean_sea_level_pressure', year, 4326)
    convertFilesToTiff(directory4, 'daily', 'surface_pressure', year, 4326)
    convertFilesToTiff(directory4, 'daily', '10m_u_component_of_wind', year, 4326)
    convertFilesToTiff(directory4, 'daily', '10m_v_component_of_wind', year, 4326)

    cmd = 'mv /Volumes/G-DRIVE\ with\ Thunderbolt/era5_t2m/tiff/daily/'+year+'/*_max.tif /Volumes/G-DRIVE\ with\ Thunderbolt/era5_maximum_2m_temperature_since_previous_post_processing/tiff/daily/'+year+'/'
    os.system(cmd)
    cmd = 'mv /Volumes/G-DRIVE\ with\ Thunderbolt/era5_t2m/tiff/daily/'+year+'/*_min.tif /Volumes/G-DRIVE\ with\ Thunderbolt/era5_minimum_2m_temperature_since_previous_post_processing/tiff/daily/'+year+'/'
    os.system(cmd)


    #Upload to GCP
    print("3rd step - Upload daily files to GCP")

    uploadToGCP(directory1,year,'daily','t2m',bucket_t2m)
    uploadToGCP(directory1,year,'daily','minimum_2m_temperature_since_previous_post_processing',bucket_mn2t)
    uploadToGCP(directory1,year,'daily','maximum_2m_temperature_since_previous_post_processing',bucket_mx2t)
    uploadToGCP(directory3,year,'daily','tp',bucket_tp)
    uploadToGCP(directory2,year,'daily','2m_dewpoint_temperature',bucket_2d)
    uploadToGCP(directory4,year,'daily','surface_pressure',bucket_sp)
    uploadToGCP(directory2,year,'daily','mean_sea_level_pressure',bucket_mslp)
    uploadToGCP(directory4,year,'daily','10m_u_component_of_wind',bucket_u10)
    uploadToGCP(directory4,year,'daily','10m_v_component_of_wind',bucket_v10)
    

    #Create manifest
    print("4th step - Create manifest of daily files")


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

    fileList=createListOfLists(directory_list,'daily',year)

    createManifestCombined_daily(fileList, year,bucket_list, directory_manifest,directory_outfile)



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