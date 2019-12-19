#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 10:13:59 2019

@author: julia_wagemann
"""

import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import glob
from osgeo import gdal, osr
import pytz
import re
import json
from google.cloud import storage
import xarray as xr

# Initiates an empty GeoTiff file
def initTiff(filename, file, noOfBands):
    outFile = gdal.GetDriverByName('GTiff').Create(filename, file.RasterXSize, file.RasterYSize, noOfBands, gdal.GDT_Float32)
    geotransform = (-180.0, 0.25, 0.0, 90.0, 0.0, -0.25)
    outFile.SetGeoTransform(geotransform)
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
#def ncToTiff_hourly(file, parameter, noOfBands, epsgCode,year):
#    ncFile = gdal.Open(file)
#    if(parameter=='tp'):
#        fileName = './tiff/'+year+'/'+file[10:28]+'.tif'
#    else:
#        fileName = './tiff/'+year+'/'+file[10:29]+'.tif'           
#    print(fileName)
#    times_ls = getEpochTimes(ncFile, noOfBands)
#    scale_factor = getScaleFactor(ncFile, parameter)
#    offset = getOffset(ncFile, parameter)
#    outTiff = initTiff(fileName,ncFile,noOfBands)
#    outBand = createTiff(ncFile, outTiff, scale_factor, offset)
#    setSpatialReference(outTiff,epsgCode)
#    outBand.FlushCache()
#    outTiff=None
#    return times_ls
    
def ncToTiff_hourly(file, noOfBands, year, epsgCode, outfile, parameter):
    if(parameter=='maximum_2m_temperature_since_previous_post_processing'):
        parameter='mx2t'
    elif(parameter=='minimum_2m_temperature_since_previous_post_processing'):
        parameter='mn2t'
    elif(parameter=='surface_pressure'):
        parameter='sp'
    elif(parameter=='2m_dewpoint_temperature'):
        parameter='d2m'
    elif(parameter=='mean_sea_level_pressure'):
        parameter='msl'
    elif(parameter=='10m_u_component_of_wind'):
        parameter='u10'
    elif(parameter=='10m_v_component_of_wind'):
        parameter='v10'
    elif(parameter=='t2m'):
        parameter='t2m'
    else:
        parameter='tp'
    ncFile = gdal.Open(file)
    outTiff = initTiff(outfile,ncFile,noOfBands)
    scale_factor = getScaleFactor(ncFile, parameter)
    offset = getOffset(ncFile, parameter)

    outBand = createTiff(ncFile, outTiff, scale_factor, offset)
    setSpatialReference(outTiff,epsgCode)
    outBand.FlushCache()
    outTiff=None


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

def convertFilesToTiff(directory, time_step, parameter, year, epsg):
    fileList = createFileList(directory, './era5_'+parameter+'/nc/'+time_step+'/'+year+'/era5_surface_pressure_1985_06_12*.nc')
    print(fileList)
    print(len(fileList))
 #   if(len(fileList)<365):
 #       return

    fileList.sort()
    for file in fileList:
        tmp = file.split('/')
        print(tmp[5][:-3])      
        outfile = directory+'era5_'+parameter+'/tiff/'+time_step+'/'+year+'/'+str(tmp[5][:-3])+'.tif'
        print(outfile)
        if(time_step!='hourly'):
            ncToTiff(file,1,year,epsg, outfile)
        else:
            ncToTiff_hourly(file,24,year, epsg,outfile,parameter)

    
def uploadMonthlyFilesToGCP(directory,parameter,year,bucket):
    fileList = createFileList(directory,'./era5_'+parameter+'/tiff/monthly/'+year+'/*08_monthly*')
    fileList.sort()
    for file in fileList:
        tmp = file.split('/')
        print(tmp)
        destname = tmp[5]
        print(destname)
        upload_blob(bucket,file,destname)

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
                             
def createManifest_hourly(eeCollectionName, assetName, parameter, bandIndex, startTime, endTime, gs_bucket,uris, year, month, day, hour):
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

def updateManifest_monthly(directory,eeCollectionName, assetName, startTime, endTime, gs_bucket_list, uris1, uris2, uris3, uris4, uris5, uris6, uris7, uris8, year, month):
    with open(directory+'manifest_structure_monthly.json','r') as f:
        jsonFile = json.load(f)

    jsonFile['name']=eeCollectionName+assetName
    jsonFile['tilesets'][0]['sources'][0]['uris']='gs://'+gs_bucket_list[0]+'/'+uris1
    jsonFile['tilesets'][1]['sources'][0]['uris']='gs://'+gs_bucket_list[1]+'/'+uris2
    jsonFile['tilesets'][2]['sources'][0]['uris']='gs://'+gs_bucket_list[2]+'/'+uris3
    jsonFile['tilesets'][3]['sources'][0]['uris']='gs://'+gs_bucket_list[3]+'/'+uris4
    jsonFile['tilesets'][4]['sources'][0]['uris']='gs://era5_tp_monthly/era5_tp_'+str(year)+'_'+str(month).zfill(2)+'_monthly_sum.tif'
    jsonFile['tilesets'][5]['sources'][0]['uris']='gs://'+gs_bucket_list[4]+'/'+uris5
    jsonFile['tilesets'][6]['sources'][0]['uris']='gs://'+gs_bucket_list[5]+'/'+uris6
    jsonFile['tilesets'][7]['sources'][0]['uris']='gs://'+gs_bucket_list[6]+'/'+uris7
    jsonFile['tilesets'][8]['sources'][0]['uris']='gs://'+gs_bucket_list[7]+'/'+uris8
    jsonFile['start_time']['seconds']=startTime
    jsonFile['end_time']['seconds']=endTime
    jsonFile['properties']['year']=year
    jsonFile['properties']['month']=month
    return jsonFile

def updateManifest_daily(directory, eeCollectionName, assetName, startTime, endTime, gs_bucket_list, uris1, uris2, uris3, uris4, uris5, uris6, uris7, uris8, year,month, day):
    with open(directory+'manifest_structure_daily.json','r') as f:
        jsonFile = json.load(f)

    jsonFile['name']=eeCollectionName+assetName
    jsonFile['tilesets'][0]['sources'][0]['uris']='gs://'+gs_bucket_list[0]+'/'+uris1
    jsonFile['tilesets'][1]['sources'][0]['uris']='gs://'+gs_bucket_list[1]+'/'+uris2
    jsonFile['tilesets'][2]['sources'][0]['uris']='gs://'+gs_bucket_list[2]+'/'+uris3
    jsonFile['tilesets'][3]['sources'][0]['uris']='gs://'+gs_bucket_list[3]+'/'+uris4
    jsonFile['tilesets'][4]['sources'][0]['uris']='gs://era5_tp_daily/era5_tp_'+str(year)+'_'+str(month).zfill(2)+'_'+str(day).zfill(2)+'_daily_sum.tif'
    jsonFile['tilesets'][5]['sources'][0]['uris']='gs://'+gs_bucket_list[4]+'/'+uris5
    jsonFile['tilesets'][6]['sources'][0]['uris']='gs://'+gs_bucket_list[5]+'/'+uris6
    jsonFile['tilesets'][7]['sources'][0]['uris']='gs://'+gs_bucket_list[6]+'/'+uris7
    jsonFile['tilesets'][8]['sources'][0]['uris']='gs://'+gs_bucket_list[7]+'/'+uris8
 #   jsonFile['tilesets'][8]['sources'][0]['uris']=gs_bucket_list[8]+uris9    
    jsonFile['start_time']['seconds']=startTime
    jsonFile['end_time']['seconds']=endTime
    jsonFile['properties']['year']=year
    jsonFile['properties']['month']=month
    jsonFile['properties']['day']=day   
    return jsonFile

def updateManifest_hourly(directory, eeCollectionName, assetName, startTime, endTime, bandIndex, gs_bucket_list, uris1, uris2, uris3, uris4, uris5, uris6, uris7, uris8, uris9, year,month, day, hour):
    with open(directory+'manifest_structure_hourly.json','r') as f:
        jsonFile = json.load(f)

    jsonFile['name']=eeCollectionName+assetName
    jsonFile['tilesets'][0]['sources'][0]['uris']='gs://'+gs_bucket_list[0]+'/'+uris1
    jsonFile['tilesets'][1]['sources'][0]['uris']='gs://'+gs_bucket_list[1]+'/'+uris2
    jsonFile['tilesets'][2]['sources'][0]['uris']='gs://'+gs_bucket_list[2]+'/'+uris3
    jsonFile['tilesets'][3]['sources'][0]['uris']='gs://'+gs_bucket_list[3]+'/'+uris4
    jsonFile['tilesets'][4]['sources'][0]['uris']='gs://'+gs_bucket_list[4]+'/'+uris5
    jsonFile['tilesets'][5]['sources'][0]['uris']='gs://'+gs_bucket_list[5]+'/'+uris6
    jsonFile['tilesets'][6]['sources'][0]['uris']='gs://'+gs_bucket_list[6]+'/'+uris7
    jsonFile['tilesets'][7]['sources'][0]['uris']='gs://'+gs_bucket_list[7]+'/'+uris8
    jsonFile['tilesets'][8]['sources'][0]['uris']='gs://'+gs_bucket_list[8]+'/'+uris9

    jsonFile['bands'][0]['tileset_band_index']=bandIndex
    jsonFile['bands'][1]['tileset_band_index']=bandIndex
    jsonFile['bands'][2]['tileset_band_index']=bandIndex
    jsonFile['bands'][3]['tileset_band_index']=bandIndex
    jsonFile['bands'][4]['tileset_band_index']=bandIndex
    jsonFile['bands'][5]['tileset_band_index']=bandIndex
    jsonFile['bands'][6]['tileset_band_index']=bandIndex
    jsonFile['bands'][7]['tileset_band_index']=bandIndex
    jsonFile['bands'][8]['tileset_band_index']=bandIndex

    jsonFile['start_time']['seconds']=startTime
    jsonFile['end_time']['seconds']=endTime
    jsonFile['properties']['year']=year
    jsonFile['properties']['month']=month
    jsonFile['properties']['day']=day 
    jsonFile['properties']['hour']=hour
    return jsonFile
    
def manifestToJSON(manifestDict, path,outFile):
    with open(path+outFile+'.json','w') as fp:
        json.dump(manifestDict,fp,indent=4)

def createFileList(directory,file_pattern):
    os.chdir(directory)
    return glob.glob(file_pattern)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    if(blob.exists()):
        print('File {} already exists'.format(destination_blob_name))
        next
    else:
        blob.upload_from_filename(source_file_name)

        print('File {} uploaded to {}.'.format(
                source_file_name,
                destination_blob_name))

def createDailyFiles(directory, parameter, year, aggregation):
#    fileList = createFileList(directory, './era5_'+parameter+'/nc/hourly/'+year+'/era5_'+parameter+'_'+year+'*')
    fileList = createFileList(directory, './era5_'+parameter+'/nc/hourly/'+year+'/era5_'+parameter+'*')
    fileList.sort()
    print(fileList)
    
    for i in range(0,len(fileList)-1):
        if(parameter=='tp'):
            array=xr.open_mfdataset([fileList[i],fileList[i+1]],concat_dim='time', combine='nested')
            print(array)
        else:
            array = xr.open_dataset(fileList[i], mask_and_scale=True, decode_times=True)
            print(array)
        tmp = fileList[i].split('/')
        print(tmp)

        outFileName = directory+'./era5_'+parameter+'/nc/daily/'+year+'/'+tmp[5][:-3]+'_daily_'+aggregation+'.nc'
        
        print(outFileName)
        if(aggregation=='mean'):
            print('mean')
            array.resample(time='1D').mean().to_netcdf(outFileName, mode='w', compute=True)
        elif(aggregation=='sum'):
            print('sum')
            array.resample(time='1D',closed='right').sum().isel(time=1).to_netcdf(outFileName, mode='w', compute=True)
        elif(aggregation=='min'):
            print('min')
            array.resample(time='1D').min().to_netcdf(outFileName, mode='w', compute=True)
        else:
            print('max')
            array.resample(time='1D').max().to_netcdf(outFileName, mode='w', compute=True)
       
def createMonthlyFiles(directory, parameter, year, aggregation):
    month_list = ['01','02','03','04','05','06','07','08','09','10','11','12']
#    month_list = ['08']
    for i in month_list:
        fileList_param = createFileList(directory,'./era5_'+parameter+'/nc/'+year+'/era5_'+parameter+'_'+year+'_'+i+'*')
        fileList_param.sort()
        print(fileList_param)
        os.chdir(directory)
        array_param = xr.open_mfdataset(fileList_param,combine='nested', concat_dim='time')
        print(array_param)
        tmp = fileList_param[0].split('/')
        outFileName_param = directory+'./era5_'+parameter+'/nc/monthly/'+year+'/'+tmp[4][:-6]+'_monthly_'+aggregation+'.nc'
        if(aggregation=='mean'):
            print('mean')
            array_param.resample(time='1M').mean().to_netcdf(outFileName_param, mode='w', compute=True)
        elif(aggregation=='sum'):
            print('sum')
            array_param.resample(time='1M').sum().to_netcdf(outFileName_param, mode='w', compute=True)
        elif(aggregation=='min'):
            print('min')
            array_param.resample(time='1M').min().to_netcdf(outFileName_param, mode='w', compute=True)
        else:
            print('max')
            array_param.resample(time='1M').max().to_netcdf(outFileName_param, mode='w', compute=True)


def uploadToGCP(directory,year,time_step,parameter,bucket):
    fileList = createFileList(directory, 'era5_'+parameter+'/tiff/'+time_step+'/'+year+'/*.tif')
    fileList.sort()

    for file in fileList:
        print(file)
        tmp = file.split('/')
        print(tmp)

        upload_blob(bucket,file,tmp[4])

def createListOfLists(directory_list,aggregation,year):
    fileList=[]
    for i in directory_list:
        os.chdir(i)
        fileList_tmp = createFileList(i,'./tiff/'+aggregation+'/'+year+'/*')
        fileList_tmp.sort()
        fileList.append(fileList_tmp)
        os.chdir('..')
    return(fileList)

def createManifestCombined(fileList, year,bucket_list, directory_manifest,directory_outfile):
    item = list(zip(*fileList))[0]
    print(item)
    for i in range(0,len(fileList[0])):
#        print(i)
        item = list(zip(*fileList))[i]
#        print(item)
        tmp = re.findall('\d+', item[0])
        assetName=tmp[3]+tmp[4]+tmp[5]
        ls_epochtimes = getEpochTimes_daily(int(tmp[3]),int(tmp[4]),int(tmp[5]))
        uris_list = []
        for i in item:
            tmp2 = i.split('/')
            uris_list.append(tmp2[4])
        manifest = updateManifest_daily(directory=directory_manifest,
                                        eeCollectionName='projects/earthengine-legacy/assets/projects/ecmwf/era5_daily/',
                                        assetName=assetName,
                                        startTime = int(ls_epochtimes[0]),
                                        endTime = int(ls_epochtimes[1]),
                                        gs_bucket_list = bucket_list,
                                        uris1=uris_list[0],
                                        uris2=uris_list[1],
                                        uris3=uris_list[2],
                                        uris4=uris_list[3],
                                        uris5=uris_list[4],
                                        uris6=uris_list[5],
                                        uris7=uris_list[6],
                                        uris8=uris_list[7],
                                        year=int(tmp[3]),
                                        month=int(tmp[4]),
                                        day=int(tmp[5]))
        outfile='manifest_'+assetName+'_daily'
        manifestToJSON(manifest,directory_outfile+year+'/',outfile)

def createManifestCombined_monthly(fileList, year,bucket_list, directory_manifest,directory_outfile):
    item = list(zip(*fileList))[0]
    print(item)
    for i in range(0,len(fileList[0])):
#        print(i)
        item = list(zip(*fileList))[i]
#        print(item)
        tmp = re.findall('\d+', item[0])
        assetName=tmp[3]+tmp[4]
        ls_epochtimes = getEpochTimes_monthly(int(tmp[3]),int(tmp[4]))
        uris_list = []
        for i in item:
            tmp2 = i.split('/')
            print(tmp2)
            uris_list.append(tmp2[4])
        manifest = updateManifest_monthly(directory=directory_manifest,
                                        eeCollectionName='projects/earthengine-legacy/assets/projects/ecmwf/era5_monthly/',
                                        assetName=assetName,
                                        startTime = int(ls_epochtimes[0]),
                                        endTime = int(ls_epochtimes[1]),
                                        gs_bucket_list = bucket_list,
                                        uris1=uris_list[0],
                                        uris2=uris_list[1],
                                        uris3=uris_list[2],
                                        uris4=uris_list[3],
                                        uris5=uris_list[4],
                                        uris6=uris_list[5],
                                        uris7=uris_list[6],
                                        uris8=uris_list[7],
                                        year=int(tmp[3]),
                                        month=int(tmp[4]))
        outfile='manifest_'+assetName+'_monthly'
        manifestToJSON(manifest,directory_outfile+year+'/',outfile)

def createManifestCombined_hourly(fileList, ncFileList, year, bucket_list, directory_manifest,directory_outfile):
    print
    for i in range(0,len(fileList[0])):
        print(len(fileList[0]))
        item = list(zip(*fileList))[i]
        print('item', item)
        tmp = re.findall('\d+', item[0])
        print(tmp)
        assetName=tmp[3]+tmp[4]+tmp[5]
        print('assetname', assetName)
        print(item[0])
        ncFile = gdal.Open(ncFileList[i])

        ls_epochtimes = getEpochTimes(ncFile,24)
        print(ls_epochtimes)
        uris_list = []
        for i in item:
             tmp2 = i.split('/')
             uris_list.append(tmp2[4])
        print(uris_list)

        for k in range(0,len(ls_epochtimes)-1):
            print(k)
            hour= str(k).zfill(2)
            manifest = updateManifest_hourly(directory=directory_manifest,
                                  eeCollectionName='projects/earthengine-legacy/assets/projects/ecmwf/era5_hourly/',
                                  assetName=assetName+'T'+hour,
                                  startTime=int(ls_epochtimes[k]),
                                  endTime=int(ls_epochtimes[k+1]),
                                  bandIndex=k,
                                  gs_bucket_list=bucket_list,
                                  uris1=uris_list[0],
                                  uris2=uris_list[1],
                                  uris3=uris_list[2],
                                  uris4=uris_list[3],
                                  uris5=uris_list[4],
                                  uris6=uris_list[5],
                                  uris7=uris_list[6],
                                  uris8=uris_list[7],
                                  uris9=uris_list[8],
                                  year=int(tmp[3]),
                                  month=int(tmp[4]),
                                  day=int(tmp[5]),
                                  hour=int(hour))
            outfile='manifest_'+assetName+hour+'_hourly'
            manifestToJSON(manifest,directory_outfile+year+'/',outfile)

