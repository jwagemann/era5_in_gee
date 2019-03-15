#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 10:29:55 2019

@author: julia_wagemann
"""
import os
from era5_in_gee_functions import createFileList

fileList = createFileList('/Volumes/FREECOM HDD/era5_tp/manifest/2000/','./manifest_2000*.json')

for i in fileList:
    print(i)
    cmd = 'earthengine --use_cloud_api upload image --manifest ' + i
    os.system(cmd)