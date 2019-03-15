#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 11:07:50 2019

@author: julia_wagemann
"""

from era5_in_gee_functions import createFileList

import os

directory='/Volumes/FREECOM HDD/era5_tp/nc/2017/'
fileList=createFileList(directory,'./era5_tp_2017_11*')
print(fileList)
for i in fileList:
    ls = i[:-3].split('_')
    ls[3]=ls[3].zfill(2)
    ls[4]=ls[4].zfill(2)
    renamed= '_'.join(ls) + '.nc'
    os.rename(i,renamed)