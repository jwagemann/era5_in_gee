#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 10:13:59 2019

@author: julia_wagemann
"""

import os
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import glob
from osgeo import gdal, osr
import pytz
import re
import json
from google.cloud import storage

# Initiates an empty GeoTiff file
def initTiff(filename, file, noOfBands):
    outFile = gdal.GetDriverByName('GTiff').Create(filename, file.RasterXSize, file.RasterYSize, noOfBands, gdal.GDT_Float32)
    outFile.SetGeoTransform(file.GetGeoTransform())
    return outFile

# add rasterbands to the GeoTiff and apply scale and offset factors
def createTiff(file, outfile, scale_factor, offset):
    for j in range(1, file.RasterCount+1):
        fileLayer = file.GetRasterBand(j).ReadAsArray().astype('float')
        finalArray = float(offset) + (fileLayer * float(scale_factor))
        finalArray[finalArray<0] = 0.0
        outBand = outfile.GetRasterBand(j)
        outBand.WriteArray(finalArray)
    return outBand

# Retrieve scale factor from a NetCDF file
def getScaleFactor(file, parameter):
    return float(file.GetMetadataItem(parameter+"#scale_factor"))

#Retrieve offset factor from a NetCDF file
def getOffset(file, parameter):
    return float(file.GetMetadataItem(parameter+"#add_offset"))

# Set spatial reference based on an EPSG code to a GeoTiff file
def setSpatialReference(file,EPSGCode):
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(EPSGCode)
    file.SetProjection(srs.ExportToWkt())

# Function that converts NetCDF file of a file list to GeoTiffs
def ncToTiff_hourly(file, parameter, noOfBands, epsgCode,year):
    ncFile = gdal.Open(file)
    if(parameter=='tp'):
        fileName = './tiff/'+year+'/'+file[10:28]+'.tif'
    else:
        fileName = './tiff/'+year+'/'+file[10:29]+'.tif'            
    print(fileName)
    times_ls = getEpochTimes(ncFile, noOfBands)
    scale_factor = getScaleFactor(ncFile, parameter)
    offset = getOffset(ncFile, parameter)
    outTiff = initTiff(fileName,ncFile,noOfBands)
    outBand = createTiff(ncFile, outTiff, scale_factor, offset)
    setSpatialReference(outTiff,epsgCode)
    outBand.FlushCache()
    outTiff=None
    return times_ls

def ncToTiff(file, noOfBands, year,epsgCode,outfile):
    outfile = outfile
    print(outfile)
    ncFile=gdal.Open(file)
    outTiff = initTiff(outfile,ncFile,noOfBands)
    fileLayer = ncFile.GetRasterBand(1).ReadAsArray().astype('float')
    fileLayer[fileLayer<0] = 0.0
    outBand = outTiff.GetRasterBand(1)
    outBand.WriteArray(fileLayer)
    setSpatialReference(outTiff, epsgCode)
    outBand.FlushCache()
    outTiff=None

def getEpochTimes(file, noOfBands):
    base = datetime(1900,1,1,0,0,0,0).replace(tzinfo=pytz.UTC)
    ls_epochtime = []
    
    for i in range(1,noOfBands+1):
        tmp = file.GetRasterBand(i)
        tmp_time = tmp.GetMetadata()['NETCDF_DIM_time']
        epoch_time = base + timedelta(hours=int(tmp_time))
        ls_epochtime.append(int(epoch_time.timestamp()))
    epoch_time = base + timedelta(hours=int(tmp_time)+1)
    ls_epochtime.append(int(epoch_time.timestamp()))
    return ls_epochtime

def getEpochTimes_daily(year,month,day):
    ls_epochtime = []
    startTime = datetime(year,month,day, tzinfo=pytz.utc)
    endTime = startTime + timedelta(days=1)
    ls_epochtime.append(startTime.timestamp())
    ls_epochtime.append(endTime.timestamp())
    return ls_epochtime

def getEpochTimes_monthly(year,month):
    ls_epochtime = []
    startTime = datetime(year,month, 1, tzinfo=pytz.utc)
    endTime = startTime + relativedelta(months=+1)
    ls_epochtime.append(startTime.timestamp())
    ls_epochtime.append(endTime.timestamp())
    return ls_epochtime

def createAssetName(string,parameter,hour):
    tmp = re.findall("\d+", string)
    assetName = str(tmp[2])+str(tmp[3])+str(tmp[4])+'T'+str(hour)+'_'+parameter
    return assetName
                             
def createManifest(eeCollectionName, assetName, parameter, bandIndex, startTime, endTime, gs_bucket,uris, year, month, day, hour):
    manifest = {}
    manifest['name']= eeCollectionName+assetName
    manifest['tilesets']={}
    manifest['tilesets']['id']='era5_'+parameter
    manifest['tilesets']['sources']={}
    manifest['tilesets']['sources']['uris']= gs_bucket+uris
    manifest['bands']={}
    manifest['bands']['id']=parameter
    manifest['bands']['tileset_band_index']=bandIndex
    manifest['bands']['tileset_id']='era5_'+parameter
    manifest['start_time']={}
    manifest['start_time']['seconds']=startTime
    manifest['end_time']={}
    manifest['end_time']['seconds']=endTime
    manifest['properties']={}
    manifest['properties']['year']=year
    manifest['properties']['month']=month
    manifest['properties']['day']=day
    manifest['properties']['hour']=hour
    return manifest

def createManifest_daily(eeCollectionName, assetName, parameter, bandIndex, startTime, endTime, gs_bucket,uris, year, month, day):
    manifest = {}
    manifest['name']= eeCollectionName+assetName
    manifest['tilesets']={}
    manifest['tilesets']['id']='era5_'+parameter
    manifest['tilesets']['sources']={}
    manifest['tilesets']['sources']['uris']= gs_bucket+uris
    manifest['bands']={}
    manifest['bands']['id']=parameter
    manifest['bands']['tileset_band_index']=bandIndex
    manifest['bands']['tileset_id']='era5_'+parameter
    manifest['start_time']={}
    manifest['start_time']['seconds']=startTime
    manifest['end_time']={}
    manifest['end_time']['seconds']=endTime
    manifest['properties']={}
    manifest['properties']['year']=year
    manifest['properties']['month']=month
    manifest['properties']['day']=day
    return manifest

def createManifest_monthly(eeCollectionName, assetName, parameter, bandIndex, startTime, endTime, gs_bucket,uris, year, month):
    manifest = {}
    manifest['name']= eeCollectionName+assetName
    manifest['tilesets']={}
    manifest['tilesets']['id']='era5_'+parameter
    manifest['tilesets']['sources']={}
    manifest['tilesets']['sources']['uris']= gs_bucket+uris
    manifest['bands']={}
    manifest['bands']['id']=parameter
    manifest['bands']['tileset_band_index']=bandIndex
    manifest['bands']['tileset_id']='era5_'+parameter
    manifest['start_time']={}
    manifest['start_time']['seconds']=startTime
    manifest['end_time']={}
    manifest['end_time']['seconds']=endTime
    manifest['properties']={}
    manifest['properties']['year']=year
    manifest['properties']['month']=month
    return manifest
    
def manifestToJSON(manifestDict, path,outFile):
    with open(path+outFile+'.json','w') as fp:
        json.dump(manifestDict,fp)

def createFileList(directory,file_pattern):
    os.chdir(directory)
    return glob.glob(file_pattern)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))