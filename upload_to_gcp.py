#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 10:19:35 2019

@author: julia_wagemann
"""

from era5_in_gee_functions import upload_blob, createFileList
import time

execTime = time.time()
bucket_name = 'era5_tp'
fileList = createFileList('/Volumes/FREECOM HDD/era5_tp/tiff/2000','era5_tp_2000*')

for i in fileList[327:]:
    print(i)
    upload_blob(bucket_name, i, i)
    
print("The script took {0} second !".format(time.time() - execTime))
