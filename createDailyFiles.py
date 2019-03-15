#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 16:42:56 2019

@author: julia_wagemann
"""

import xarray as xr
from era5_in_gee_functions import createFileList
import time

execTime = time.time()

directory = '/Volumes/FREECOM HDD/era5_tp/nc/'
fileList = createFileList(directory,'./1981/era5_tp_1981*')
print(fileList)


for file in fileList:
    array = xr.open_dataset(file, mask_and_scale=True, decode_times=True)
    outFileName = directory+'/daily/1981/'+file[7:-3]+'_daily.nc'
    print(outFileName)
    array.resample(time='1D').sum().to_netcdf(outFileName, mode='w', compute=True)

print("The script took {0} second !".format(time.time() - execTime))


