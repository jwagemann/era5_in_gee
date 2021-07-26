#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 15:46:02 2019

@author: julia_wagemann
"""

from era5_in_gee_functions import createFileList, createListOfLists, createMonthlyFiles, convertFilesToTiff, uploadMonthlyFilesToGCP, createManifestCombined_monthly, ee_ingest
import time



execTime = time.time()

############################################

directory1 = '/Volumes/G-Drive with Thunderbolt/'
directory2 = '/Volumes/jules_eh2/'
directory3 = '/Volumes/FREECOM HDD/'
directory4 = '/Volumes/LaCie/'

#yearList=['1990','1991','1992','1993','1994','1995','1996','1997','1998','1999']
#yearList=['2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010']
yearList=['2020']          #'2011','2012','2013','2014','2015','2016','2017','2018','2019']
#yearList=['1979','1980','1981','1982','1983','1984','1985','1986','1987','1988','1989']

bucket = 'earthengine-ecmwf'
bucket_t2m = bucket+'/era5/monthly/era5_t2m'
bucket_tp = bucket+'/era5/monthly/era5_tp'
bucket_mx2t = bucket+'/era5/monthly/era5_mx2t'
bucket_mn2t = bucket+'/era5/monthly/era5_mn2t'
bucket_sp = bucket+'/era5/monthly/era5_sp'
bucket_mslp = bucket+'/era5/monthly/era5_msl'
bucket_2d = bucket+'/era5/monthly/era5_d2m'
bucket_u10 = bucket+'/era5/monthly/era5_u10'
bucket_v10 = bucket+'/era5/monthly/era5_v10'

directory_manifest = '/Volumes/G-Drive with Thunderbolt/manifests/'
directory_outfile = '/Volumes/G-Drive with Thunderbolt/manifests/era5_monthly/'

############################################

for year in yearList:

    print('1st step - Create monthly files')

 #   createMonthlyFiles(directory1, 't2m', year, 'mean')
 #   createMonthlyFiles(directory1, 't2m', year, 'min')
 #   createMonthlyFiles(directory1, 't2m', year, 'max')
 #   createMonthlyFiles(directory1, 'tp', year, 'sum')
 #   createMonthlyFiles(directory1, 'minimum_2m_temperature_since_previous_post_processing', year, 'min')
 #   createMonthlyFiles(directory1, 'maximum_2m_temperature_since_previous_post_processing', year, 'max')
 #   createMonthlyFiles(directory1, '2m_dewpoint_temperature',year,'mean')
   # createMonthlyFiles(directory1, 'mean_sea_level_pressure',year,'mean')
 #   createMonthlyFiles(directory1, 'surface_pressure',year,'mean')
 #   createMonthlyFiles(directory1, '10m_u_component_of_wind',year,'mean')
 #   createMonthlyFiles(directory1, '10m_v_component_of_wind',year,'mean')


    print('2nd step - Convert monthly files to tiffs')

 #   convertFilesToTiff(directory1,'monthly','t2m',year,4326)
#    convertFilesToTiff(directory1,'monthly','tp',year,4326)
    # converFilesToTiff(directory1,'minimum_2m_temperature_since_previous_post_processing',4326)
    # convertFilesToTiff(directory1,'maximum_2m_temperature_since_previous_post_processing',4326)
#    convertFilesToTiff(directory1, 'monthly', '2m_dewpoint_temperature', year, 4326)
#    convertFilesToTiff(directory1, 'monthly', 'mean_sea_level_pressure', year, 4326)
#    convertFilesToTiff(directory1, 'monthly', 'surface_pressure', year, 4326)
#    convertFilesToTiff(directory1, 'monthly', '10m_u_component_of_wind', year, 4326)
#    convertFilesToTiff(directory1, 'monthly', '10m_v_component_of_wind', year, 4326)



    print("3rd step - Upload monthly files to GCP")

    #uploadMonthlyFilesToGCP(directory1,'t2m',year,bucket, bucket_t2m)
#    uploadMonthlyFilesToGCP(directory1,'tp',year,bucket,bucket_tp)
#    uploadMonthlyFilesToGCP(directory1, 'minimum_2m_temperature_since_previous_post_processing', year, bucket, bucket_mn2t)
#    uploadMonthlyFilesToGCP(directory1, 'maximum_2m_temperature_since_previous_post_processig', year, bucket, bucket_mx2t)

#    uploadMonthlyFilesToGCP(directory1,'2m_dewpoint_temperature',year,bucket, bucket_2d)
#    uploadMonthlyFilesToGCP(directory1,'surface_pressure',year,bucket, bucket_sp)
#    uploadMonthlyFilesToGCP(directory1,'mean_sea_level_pressure',year, bucket, bucket_mslp)
#    uploadMonthlyFilesToGCP(directory1,'10m_u_component_of_wind',year, bucket, bucket_u10)
#    uploadMonthlyFilesToGCP(directory1,'10m_v_component_of_wind',year, bucket, bucket_v10)


    # print('4th step - Create manifests')

    # directory_list=[directory1+'/era5_t2m/',
    #                 directory1+'/era5_minimum_2m_temperature_since_previous_post_processing',
    #                   directory1+'/era5_maximum_2m_temperature_since_previous_post_processing',
    #                   directory1+'/era5_2m_dewpoint_temperature',
    #                   directory1+'/era5_tp',
    #                   directory1+'/era5_surface_pressure',
    #                   directory1+'/era5_mean_sea_level_pressure',
    #                   directory1+'/era5_10m_u_component_of_wind',
    #                   directory1+'/era5_10m_v_component_of_wind']

    # # # print(directory_list)
    # bucket_list=[bucket_t2m, bucket_mn2t, bucket_mx2t, bucket_2d, bucket_tp, bucket_sp, bucket_mslp, bucket_u10, bucket_v10]
    # print(bucket_list)
    # fileList=createListOfLists(directory_list,'monthly',year)
    # print(fileList)

    # createManifestCombined_monthly(fileList, year,bucket_list, directory_manifest,directory_outfile)


 #   Ingest to EE
    print("5th step - Ingest to EE")

    manifest_list = createFileList(directory_outfile+year+'/', '*')
    print(year)
    print(manifest_list)
    ee_ingest(manifest_list)


print("The script took {0} second !".format(time.time() - execTime))
