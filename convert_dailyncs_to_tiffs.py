#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 16:55:51 2019

@author: julia_wagemann
"""

from era5_in_gee_functions import createFileList, ncToTiff
import re

directory='/Volumes/FREECOM HDD/era5_tp/'
pattern='./nc/daily/1981/*.nc'

fileList = createFileList(directory,pattern)
fileList.sort()
print(fileList)


for file in fileList:
    print(file)
    tmp1 = re.findall("\d+", file)
    year = tmp1[2]
    outfile =  directory+'tiff/daily/'+year+'/'+file[16:-3]+'.tif'
    ncToTiff(file, 1,year,4326,outfile)



