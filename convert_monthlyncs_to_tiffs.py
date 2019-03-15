#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 13:25:20 2019

@author: julia_wagemann
"""

from era5_in_gee_functions import createFileList,ncToTiff
import re

directory='/Volumes/FREECOM HDD/era5_tp/'
pattern='./nc/monthly/1981/*.nc'

fileList = createFileList(directory,pattern)
fileList.sort()
print(fileList)


for file in fileList:
    print(file)
    tmp1 = re.findall("\d+", file)
    year = tmp1[2]
    outfile = directory+'tiff/monthly/'+year+'/'+file[18:-3]+'.tif'
    ncToTiff(file, 1,year,4326, outfile)