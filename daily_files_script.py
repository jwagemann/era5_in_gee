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
#yearList = ['1987','1988','1989']
#yearList = ['2000']
# yearList = ['2018','2019']
#yearList = ['2014','2015','2016','2017','2018','2019']
yearList = ['2019']

bucket = 'earthengine-ecmwf'
bucket_t2m = bucket+'/era5/daily/era5_t2m'
bucket_tp = bucket+'/era5/daily/era5_tp'
bucket_mx2t = bucket+'/era5/daily/era5_mx2t'
bucket_mn2t = bucket+'/era5/daily/era5_mn2t'
bucket_sp = bucket+'/era5/daily/era5_sp'
bucket_mslp = bucket+'/era5/daily/era5_msl'
bucket_2d = bucket+'/era5/daily/era5_d2m'
bucket_u10 = bucket+'/era5/daily/era5_u10'
bucket_v10 = bucket+'/era5/daily/era5_v10'

directory_manifest = '/Volumes/G-Drive with Thunderbolt/manifests/'
directory_outfile = '/Volumes/G-Drive with Thunderbolt/manifests/era5_daily/'

############################################

for year in yearList:

#     print("1st step - Resample hourly information to daily aggregates")
     print(year)
#     createDailyFiles(directory1,'t2m',year,'mean')
#     createDailyFiles(directory1,'t2m',year,'min')
#     createDailyFiles(directory1,'t2m',year,'max')
 #    createDailyFiles(directory1, 'tp',year,'sum')
     # createDailyFiles(directory1, '2m_dewpoint_temperature',year,'mean')
     # createDailyFiles(directory1, 'mean_sea_level_pressure',year,'mean')
     # createDailyFiles(directory1, 'surface_pressure',year,'mean')
     # createDailyFiles(directory1, '10m_u_component_of_wind',year,'mean')
     # createDailyFiles(directory1, '10m_v_component_of_wind',year,'mean')

# #    #Convert daily files to tiffs
#     print("2nd step - Convert daily files to tiffs")
#     convertFilesToTiff(directory1, 'daily', 't2m', year, 4326)
 #    convertFilesToTiff(directory1, 'daily', 'tp', year, 4326)
     # convertFilesToTiff(directory1, 'daily', '2m_dewpoint_temperature', year, 4326)
     # convertFilesToTiff(directory1, 'daily', 'mean_sea_level_pressure', year, 4326)
     # convertFilesToTiff(directory1, 'daily', 'surface_pressure', year, 4326)
     # convertFilesToTiff(directory1, 'daily', '10m_u_component_of_wind', year, 4326)
     # convertFilesToTiff(directory1, 'daily', '10m_v_component_of_wind', year, 4326)

     # cmd = 'mv /Volumes/G-DRIVE\ with\ Thunderbolt/era5_t2m/tiff/daily/'+year+'/*_max.tif /Volumes/G-DRIVE\ with\ Thunderbolt/era5_maximum_2m_temperature_since_previous_post_processing/tiff/daily/'+year+'/'
     # os.system(cmd)
     # cmd = 'mv /Volumes/G-DRIVE\ with\ Thunderbolt/era5_t2m/tiff/daily/'+year+'/*_min.tif /Volumes/G-DRIVE\ with\ Thunderbolt/era5_minimum_2m_temperature_since_previous_post_processing/tiff/daily/'+year+'/'
     # os.system(cmd)


#     #Upload to GCP
#     print("3rd step - Upload daily files to GCP")

     # uploadToGCP(directory1,year,'daily','t2m',bucket)
     # uploadToGCP(directory1,year,'daily','minimum_2m_temperature_since_previous_post_processing',bucket)
     # uploadToGCP(directory1,year,'daily','maximum_2m_temperature_since_previous_post_processing',bucket)
  #   uploadToGCP(directory1,year,'daily','tp',bucket)
     # uploadToGCP(directory1,year,'daily','2m_dewpoint_temperature',bucket)
     # uploadToGCP(directory1,year,'daily','surface_pressure',bucket)
     # uploadToGCP(directory1,year,'daily','mean_sea_level_pressure',bucket)
     # uploadToGCP(directory1,year,'daily','10m_u_component_of_wind',bucket)
     # uploadToGCP(directory1,year,'daily','10m_v_component_of_wind',bucket)
    

    # #Create manifest
    #  print("4th step - Create manifest of daily files")


     directory_list=[directory1+'/era5_t2m/',
                        directory1+'/era5_minimum_2m_temperature_since_previous_post_processing',
                        directory1+'/era5_maximum_2m_temperature_since_previous_post_processing',
                        directory1+'/era5_2m_dewpoint_temperature',
                        directory1+'/era5_tp',
                        directory1+'/era5_surface_pressure',
                        directory1+'/era5_mean_sea_level_pressure',
                        directory1+'/era5_10m_u_component_of_wind',
                        directory1+'/era5_10m_v_component_of_wind']
     print(directory_list)
     bucket_list=[bucket_t2m, bucket_mn2t, bucket_mx2t, bucket_2d, bucket_tp, bucket_sp, bucket_mslp, bucket_u10, bucket_v10]

     fileList=createListOfLists(directory_list,'daily',year)

     createManifestCombined_daily(fileList, year,bucket_list, directory_manifest,directory_outfile)

#

    # #Ingest to EE
    # print("5th step - Ingest to EE")

    #  manifest_list = createFileList(directory_outfile+year+'/', 'manifest_201912*')
    #  print(year)
    #  # print(len(manifest_list))

    # # if(len(manifest_list)<365 and year!='2019'):
    # #     break
    # # else:
    #  ee_ingest(manifest_list)
    


print("The script took {0} second !".format(time.time() - execTime))


