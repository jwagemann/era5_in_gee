# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from google.cloud import storage
import glob
import os

bucket_name = 'era5_t2m'
"/Volumes/FREE
directory = #path to the directory with the grib files

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

def createFileList(directory,file_pattern):
    os.chdir(directory)
    return glob.glob(file_pattern)

fileList = createFileList(directory, '/*.grib')
fileList.sort()

for i in fileList:
    print(i)
    upload_blob(bucket_name, i, i)
