#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 17:29:33 2019

@author: julia_wagemann
"""

# Import libraries
from google.cloud import storage

#############################################################################

bucket_t2m = 'era5_t2m_daily'
bucket_tp = 'era5_tp_daily'
bucket_mx2t = 'era5_mx2t_daily'
bucket_mn2t = 'era5_mn2t_daily'
bucket_sp = 'era5_sp_daily'
bucket_mslp = 'era5_mslp_daily'
bucket_2d = 'era5_2d_daily'
bucket_u10 = 'era5_u10_daily'
bucket_v10 = 'era5_v10_daily'

year='2005'

#############################################################################


# Delete a blob subset of a bucket
storage_client = storage.Client()
bucket = storage_client.get_bucket(bucket_tp)
blob_list = list(bucket.list_blobs(prefix='era5_tp_2005'))

print(blob_list)
bucket.delete_blobs(blob_list)
print('Files from GCP deleted')


# Delete entire content of a bucket
bucket_list=[bucket_tp]
print(bucket_list)

storage_client = storage.Client()

for i in bucket_list:
    print(i)
    bucket = storage_client.get_bucket(i)
    if(i==bucket_mx2t):
        prefix='era5_t2m_'
        blob_list = list(bucket.list_blobs(prefix=prefix+year))
    elif(i==bucket_mn2t):
            prefix='era5_t2m_'
            blob_list = list(bucket.list_blobs(prefix=prefix+year))
    elif(i==bucket_2d):
        prefix='era5_2m_dewpoint_temperature_'
        blob_list = list(bucket.list_blobs(prefix=prefix+year))
    elif(i==bucket_mslp):
        prefix='era5_mean_sea_level_pressure_'
        blob_list = list(bucket.list_blobs(prefix=prefix+year))
    elif(i==bucket_sp):
        prefix='era5_surface_pressure_'
        blob_list = list(bucket.list_blobs(prefix=prefix+year))
    elif(i==bucket_u10):
        prefix='era5_10m_u_component_of_wind_'
        blob_list = list(bucket.list_blobs(prefix=prefix+year))
    elif(i==bucket_v10):
        prefix='era5_10m_v_component_of_wind_'
        blob_list = list(bucket.list_blobs(prefix=prefix+year))
    else:
        blob_list = list(bucket.list_blobs(prefix=i[:-5]+year))
    print(blob_list)
    bucket.delete_blobs(blob_list)
    print('Files from GCP deleted')