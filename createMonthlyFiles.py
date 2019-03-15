#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 11:00:05 2019

@author: julia_wagemann
"""

import xarray as xr
from era5_in_gee_functions import createFileList
import time

execTime = time.time()

directory = '/Volumes/FREECOM HDD/era5_tp/nc/1981/'
month_list = ['01','02','03','04','05','06','07','08','09','10','11','12']
for i in month_list:
    fileList = createFileList(directory,'./era5_tp_1981_'+i+'*')
    fileList.sort()
    print(fileList)

    array = xr.open_mfdataset(fileList)
    outFileName = '/Volumes/FREECOM HDD/era5_tp/nc/monthly/1981/era5_tp_1981_'+i+'.nc'
    array.resample(time='1M').sum().to_netcdf(outFileName, mode='w', compute=True)

print("The script took {0} second !".format(time.time() - execTime))

