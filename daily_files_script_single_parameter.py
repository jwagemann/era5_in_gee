#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:02:16 2019

@author: julia_wagemann
"""


from era5_in_gee_functions import createFileList, createDailyFiles, convertFilesToTiff, uploadToGCP, createManifestCombined_daily, createListOfLists, ee_ingest, getEpochTimes_daily,updateManifest_daily_single_variable, manifestToJSON
import time
import re
import os

###########################################

execTime = time.time()

# General path to directory where files and manifests are stored
directory1 = '/Volumes/G-Drive with Thunderbolt/'

yearList = ['1980']

# Name of GCP bucket
bucket = 'earthengine-ecmwf'
# Sub-path of GCP bucket
bucket_t2m = bucket+'/era5/daily/era5_t2m'

# Directory path to manifest templates
directory_manifest = directory1+'manifests/'
# Directory path to folder, where manifests shall be stored
directory_outfile = directory1+'/manifests/era5_daily/'

############################################

for year in yearList:

#     print("1st step - Resample hourly information to daily aggregates")
     print(year)
#     createDailyFiles(directory1,'t2m',year,'mean')


     #Convert daily files to tiffs
#     print("2nd step - Convert daily files to tiffs")
#     convertFilesToTiff(directory1, 'daily', 't2m', year, 4326)


     #Upload to GCP
#     print("3rd step - Upload daily files to GCP")

   #  uploadToGCP(directory1,year,'daily','t2m',bucket)

    

     #Create manifest
     print("4th step - Create manifest of daily files")

    # Directory where tiff files are stored
     directory=directory1+'/era5_t2m/tiff/daily/'+year+'/'

    #Create list of all tiff files that shall be ingested
     fileList=createFileList(directory, '*.tif')
     print(fileList)
     for i in fileList:
         # Split name of file and find all numbers
          tmp = re.findall('\d+', i)
          print(tmp)
          # Create name of asset based on year month day info
          assetName=tmp[2]+tmp[3]+tmp[4]
          print(assetName)
        
         # Get start and end times of the asset in epoch times
          ls_epochtimes = getEpochTimes_daily(int(tmp[2]),int(tmp[3]),int(tmp[4]))
          print(ls_epochtimes)

         # Define start and end time
          startTime=int(ls_epochtimes[0])
          endTime=int(ls_epochtimes[1])

          # Define name of asset folder in Earth Engine
          eeCollectionName='projects/earthengine-legacy/assets/projects/ecmwf/era5_daily_test/'
          uris1=i

          manifest = updateManifest_daily_single_variable(directory_manifest,
                                                eeCollectionName,
                                                assetName,
                                                startTime,
                                                endTime,
                                                bucket_t2m,
                                                uris1,
                                                int(tmp[2]),
                                                int(tmp[3]),
                                                int(tmp[4]))

        # Create name of individual manifests
          outfile='manifest_'+assetName+'_daily_single_test'

          # Store manifest info as JSON
          manifestToJSON(manifest,directory_outfile+year+'/',outfile)


     #Ingest to EE
     print("5th step - Ingest to EE")

    # Create list of manifest files that shall be ingested
     manifest_list = createFileList(directory_outfile+year+'/', '*test.json')
    # Ingest assets based on manifest
     ee_ingest(manifest_list)
    


print("The script took {0} second !".format(time.time() - execTime))


