#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Last modified: 19 December 2019

@author: julia_wagemann
"""


# Load required libaries
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


################################################################################
# Useful data handling functions
################################################################################

def createFileList(directory,file_pattern):
    ''' Creates a list of files based on a given file pattern
    
    Parameters:
    directory (str): Path to the file directory
    file_pattern (str): File pattern of files to be included in the list
    
    Returns:
    list: List of files
    '''
    os.chdir(directory)
    return glob.glob(file_pattern)

def createListOfLists(directory_list,aggregation,year):
    ''' Creates a list of lists to create manifests with multiple variables
    
    Parameters:
    directory_list (list): List of directory paths to tiff files
    aggregation (str): string indicating the aggregation level, e.g. daily to be appended to the directory paths
    year (str): year for which the list is created
    
    Returns:
    fileList: List of tiff file lists (all parameters that shall be part of one EE asset)
    '''
    fileList=[]
    for i in directory_list:
        os.chdir(i)
        # Create a file list for each entry of the directory list
        fileList_tmp = createFileList(i,'./tiff/'+aggregation+'/'+year+'/*')
        # Sort the resulting file list
        fileList_tmp.sort()
        # Append to build up a list of lists
        fileList.append(fileList_tmp)
        os.chdir('..')
    return(fileList)


def getEpochTimes(file, noOfBands):
    ''' Converts the time information of a NetCDF file with 24 hourly time stamps from the Climate Data Store into 
    a list of epoch time stamps, which are required to ingest an asset to Earth Engine.
    
    Parameters:
    file (netCDF4 Dataset): netCDF4 Dataset object
    noOfBands (int): number of time stamps of the NetCDF Dataset
    
    Returns:
    ls_epochtime (list): list of converted epoch time stamps
    '''   
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
    ''' Converts the time information given with year, month and day to the equivalent epoch time stamp.
    
    Parameters:
    year (int): year
    month (int): month
    day (int): day
    
    Returns:
    ls_epochtime (list): Converted epoch time stamps for start and end time of the asset
    ''' 
    ls_epochtime = []
    startTime = datetime(year,month,day, tzinfo=pytz.utc)
    endTime = startTime + timedelta(days=1)
    ls_epochtime.append(startTime.timestamp())
    ls_epochtime.append(endTime.timestamp())
    return ls_epochtime

def getEpochTimes_monthly(year,month):
    ''' Converts the time information given with year and month to the equivalent epoch time stamp.
    
    Parameters:
    year (int): year
    month (int): month
    
    Returns:
    ls_epochtime (list): Converted epoch time stamps for start and end time of the asset
    ''' 
    ls_epochtime = []
    startTime = datetime(year,month, 1, tzinfo=pytz.utc)
    endTime = startTime + relativedelta(months=+1)
    ls_epochtime.append(startTime.timestamp())
    ls_epochtime.append(endTime.timestamp())
    return ls_epochtime


################################################################################
# Functions to generate a GeoTiff with gdal
################################################################################


def initTiff(filename, file, noOfBands):
    ''' Initializes a tiff file based on a given NetCDF file and a geotransform object with 0.25 deg / 0.25 deg resolution.
    
    Parameters:
    filename (str): name of the resulting GeoTiff file
    file (NetCDF object): NetCDF object open with gdal.Open(file)
    noOfBands (int): number of bands of the resulting GeoTiff
    
    Returns:
    outFile (gdal TIFF object): returns a Tiff file object that can be used to write array information with func(createTiff)
    ''' 
    outFile = gdal.GetDriverByName('GTiff').Create(filename, file.RasterXSize, file.RasterYSize, noOfBands, gdal.GDT_Float32)
    geotransform = (-180.0, 0.25, 0.0, 90.0, 0.0, -0.25)
    outFile.SetGeoTransform(geotransform)
    return outFile


def createTiff(file, outfile, scale_factor, offset):
    ''' Writes array information (raster bands) from a NetCDF file to a Tiff object which was initialized with func(initTiff).
    
    Parameters:
    file (NetCDF file object): NetCDF file object opened with gdal.Open()
    outFile (GeoTiff object): GeoTiff object initialized with func(initTiff)
    scale_factor: scale factor of the NetCDF file retrieved with func(getScaleFactor)
    offset: offset value of the NetCDF file retrieved with func(getOffset)
    
    Returns:
    outBand (gdal TIFF object): returns a Tiff file object that can be saved with .FlushCashe()
    ''' 
    for j in range(1, file.RasterCount+1):
        fileLayer = file.GetRasterBand(j).ReadAsArray().astype('float')
        finalArray = float(offset) + (fileLayer * float(scale_factor))
        finalArray[finalArray<0] = 0.0
        outBand = outfile.GetRasterBand(j)
        outBand.WriteArray(finalArray)
    return outBand


def getScaleFactor(file, parameter):
    ''' Returns the scale factor from a NetCDF file as float
    
    Parameters:
    file (NetCDF file object): NetCDF file object opened with gdal.Open()
    parameter (str): Specify the parameter of the data values
    
    Returns:
    scale factor as float
    '''
    return float(file.GetMetadataItem(parameter+"#scale_factor"))


def getOffset(file, parameter):
    ''' Returns the offset from a NetCDF file as float
    
    Parameters:
    file (NetCDF file object): NetCDF file object opened with gdal.Open()
    parameter (str): Specify the parameter of the data values
    
    Returns:
    offset as float
    '''
    return float(file.GetMetadataItem(parameter+"#add_offset"))


def setSpatialReference(file,EPSGCode):
    ''' Sets the spatial reference to a GeoTiff object initiated with func(initTiff)
    
    Parameters:
    file (GeoTiff object): GeoTiff object initiated with func(initTiff)
    EPSGCode(int): epsg code of the resulting spatial reference
    '''
    # Initiate a SpatialReference object
    srs = osr.SpatialReference()
    # Retrieve the spatial reference information from an epsg code
    srs.ImportFromEPSG(EPSGCode)
    # Set the spatial reference object to the GeoTiff file
    file.SetProjection(srs.ExportToWkt())


################################################################################
# Functions to convert NetCDF files to GeoTiffs
################################################################################


def ncToTiff(file, noOfBands, epsgCode,outfile):
    ''' Function that combines various steps to convert an aggregated NetCDF file (daily or monthly) to a GeoTiff file. Scale and Offset factors do not
    need to be applied, as those were already accounted for while the data was aggregated with xarray. See funct(createDailyFiles)
    or func(createMonthlyFiles).
    
    Parameters:
    file (str): Path to a NetCDF file
    noOfBands (int): number of bands of the resulting GeoTiff file
    epsgCode(int): epsc code number
    outfile(str): Name of resulting GeoTiff file
    '''
    # Open a NetCDF file
    ncFile=gdal.Open(file)
    # Initiate a GeoTiff object
    outTiff = initTiff(outfile,ncFile,noOfBands)
    
    fileLayer = ncFile.GetRasterBand(1).ReadAsArray().astype('float')
    fileLayer[fileLayer<0] = 0.0
    outBand = outTiff.GetRasterBand(1)
    outBand.WriteArray(fileLayer)
    # Set spatial reference to the GeoTiff object
    setSpatialReference(outTiff, epsgCode)
    # Write the GeoTiff file and close it
    outBand.FlushCache()
    outTiff=None
    
def ncToTiff_hourly(file, noOfBands, epsgCode, outfile, parameter):
    ''' Function that combines various steps to convert a NetCDF file with 24 hourly time steps to a GeoTiff file
    with 24 bands. Scale and Offset factors are applied during the conversion.
    
    Parameters:
    file (str): Path to a NetCDF file
    noOfBands (int): number of bands of the resulting GeoTiff file
    epsgCode(int): epsc code number
    outfile(str): Name of resulting GeoTiff file
    parameter(str): name of the parameter in the NetCDF file
    '''
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

def convertFilesToTiff(directory, time_step, parameter, year, epsg):
    ''' Function that loops through a directory with NetCDF files and converts the files to GeoTiff files. Calls the
    functions 'ncToTiff' or 'ncToTiff_hourly'.
    
    Parameters:
    directory (str): Path to directory with NetCDF files
    time_step (str): additon to the directory path differentiating between different aggregation levels
    parameter(str): additon to the directory path to specify the parameter
    year(str): additional to the directory path to differentiate the year
    epsg(str): epsg code of the resulting GeoTiff file
    '''
    fileList = createFileList(directory, './era5_'+parameter+'/nc/'+time_step+'/'+year+'/era5_surface_pressure_1985_06_12*.nc')
    # Test if a file of one year is missing
    if(len(fileList)<365):
        return

    fileList.sort()
    for file in fileList:
        tmp = file.split('/')
        print(tmp[5][:-3])
        # Generate name of the outfile
        outfile = directory+'era5_'+parameter+'/tiff/'+time_step+'/'+year+'/'+str(tmp[5][:-3])+'.tif'
        print(outfile)
        if(time_step!='hourly'):
            # if daily or monthly files are converted, use func(ncToTiff) else func(ncToTiff_hourly)
            ncToTiff(file,1,year,epsg, outfile)
        else:
            ncToTiff_hourly(file,24,year, epsg,outfile,parameter)

 
################################################################################
# Functions to temporarily aggregate data
################################################################################

def createDailyFiles(directory, parameter, year, aggregation):
    ''' Function that loops over a list of daily NetCDF files with 24 time stamps and aggregates (resamples) the files
    to the daily mean, sum, min or maximum. For precipitation, two NetCDF files are loaded, a ERA5 Total precipitation 
    is a forecast parameter. This means that the precipitation of the 00 time stamp is the accumulation of the rain fallen
    between 23 and 00. Thus, we need to retrieve the data of the first time step of the following file.
    
    Parameters:
    directory (str): Path to directory with NetCDF files
    parameter (str): parameter to be resampled. If 'tp', aggregation will be based on two NetCDF files
    year(str): addition to the directory path
    aggregation(str): what type of aggregation shall be executed - mean, min, max, sum
    '''    
    fileList = createFileList(directory, './era5_'+parameter+'/nc/hourly/'+year+'/era5_'+parameter+'_'+year+'*')
    fileList.sort()
    
    for i in range(0,len(fileList)-1):
        # if paramter if total precipitation, open two subsequent NetCDF files and concat the files on the time dimension
        if(parameter=='tp'):
            array=xr.open_mfdataset([fileList[i],fileList[i+1]],concat_dim='time', combine='nested')
            print(array)
        else:
        # else, open the NetCDF file and apply automatically scale and offset factors by setting the kwarg mask_and_scale=True
            array = xr.open_dataset(fileList[i], mask_and_scale=True, decode_times=True)
            print(array)
        tmp = fileList[i].split('/')

        # Define the name of the aggregated NetCDF file
        outFileName = directory+'./era5_'+parameter+'/nc/daily/'+year+'/'+tmp[5][:-3]+'_daily_'+aggregation+'.nc'
        
        print(outFileName)
        
        # Offer different aggregation methods and aggregate on a daily basis
        if(aggregation=='mean'):
            print('mean')
            array.resample(time='1D').mean().to_netcdf(outFileName, mode='w', compute=True)

        # Total precipitation values are summed over one day. By setting the keyword argument "closed='right'", xarray
        # automatically drops the first time step of the first day and takes the first time of the next day
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
    ''' Function that loops over a list of daily NetCDF files with 24 time stamps and aggregates (resamples) the files
    to the monthly mean, sum, min or maximum.
    
    Parameters:
    directory (str): Path to directory with NetCDF files
    parameter (str): parameter to be resampled. If 'tp', aggregation will be based on two NetCDF files
    year(str): addition to the directory path
    aggregation(str): what type of aggregation shall be executed - mean, min, max, sum
    ''' 
    month_list = ['01','02','03','04','05','06','07','08','09','10','11','12']

    for i in month_list:
        fileList_param = createFileList(directory,'./era5_'+parameter+'/nc/'+year+'/era5_'+parameter+'_'+year+'_'+i+'*')
        fileList_param.sort()

        os.chdir(directory)
        array_param = xr.open_mfdataset(fileList_param,combine='nested', concat_dim='time')

        tmp = fileList_param[0].split('/')
        outFileName_param = directory+'./era5_'+parameter+'/nc/monthly/'+year+'/'+tmp[4][:-6]+'_monthly_'+aggregation+'.nc'

        # Account for different aggregation levels
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



################################################################################
# Functions to create / update manifests
################################################################################

def updateManifest_hourly(directory, eeCollectionName, assetName, startTime, endTime, bandIndex, gs_bucket_list, uris1, uris2, uris3, uris4, uris5, uris6, uris7, uris8, uris9, year,month, day, hour):
    ''' Function that opens an example manifest structure file for ERA5 hourly assets and updates the dictionary items
    accordingly.
    
    Parameters:
    directory (str): Path to directory with NetCDF files
    eeCollectionName(str):  Path to collection name on Earth Engine
    assetName(str): name of resulting asset in Earth Engine
    startTime(int): start time in epoch time
    endTime(int): end time in epoch time
    bandIndex(int): number of band
    gs_bucket_list: list of GCP buckets holding the tiff files that shall be part of the asset
    uris1-uris9 (str): name of various tiff files uploaded to GCP
    year(str): add as additional asset information - year
    month(str): add as additional asset information - month
    day(str): add as additional asset information - year
    hour(str): add as additional asset information - year
    
    Returns:
    jsonFile object
    ''' 
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

def updateManifest_daily(directory, eeCollectionName, assetName, startTime, endTime, gs_bucket_list, uris1, uris2, uris3, uris4, uris5, uris6, uris7, uris8, uris9, year,month, day):
    ''' Function that opens an example manifest structure file for ERA5 daily assets and updates the dictionary items
    accordingly.
    
    Parameters:
    directory (str): Path to directory with NetCDF files
    eeCollectionName(str):  Path to collection name on Earth Engine
    assetName(str): name of resulting asset in Earth Engine
    startTime(int): start time in epoch time
    endTime(int): end time in epoch time
    gs_bucket_list: list of GCP buckets holding the tiff files that shall be part of the asset
    uris1-uris9 (str): name of various tiff files uploaded to GCP
    year(str): add as additional asset information - year
    month(str): add as additional asset information - month
    day(str): add as additional asset information - year
    
    Returns:
    jsonFile object
    ''' 
    with open(directory+'manifest_structure_daily.json','r') as f:
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
    jsonFile['start_time']['seconds']=startTime
    jsonFile['end_time']['seconds']=endTime
    jsonFile['properties']['year']=year
    jsonFile['properties']['month']=month
    jsonFile['properties']['day']=day   
    return jsonFile

def updateManifest_monthly(directory,eeCollectionName, assetName, startTime, endTime, gs_bucket_list, uris1, uris2, uris3, uris4, uris5, uris6, uris7, uris8, uris9, year, month):
    ''' Function that opens an example manifest structure file for ERA5 monthly assets and updates the dictionary items
    accordingly.
    
    Parameters:
    directory (str): Path to directory with NetCDF files
    eeCollectionName(str):  Path to collection name on Earth Engine
    assetName(str): name of resulting asset in Earth Engine
    startTime(int): start time in epoch time
    endTime(int): end time in epoch time
    gs_bucket_list: list of GCP buckets holding the tiff files that shall be part of the asset
    uris1-uris9 (str): name of various tiff files uploaded to GCP
    year(str): add as additional asset information - year
    month(str): add as additional asset information - month
    
    Returns:
    jsonFile object
    ''' 
    
    with open(directory+'manifest_structure_monthly.json','r') as f:
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
    jsonFile['start_time']['seconds']=startTime
    jsonFile['end_time']['seconds']=endTime
    jsonFile['properties']['year']=year
    jsonFile['properties']['month']=month
    return jsonFile
    
    
def manifestToJSON(manifestDict, path,outFile):
    ''' Function that dumps a json file object and creates a JSON file
    
    Parameters:
    manifestDict(json object):
    path(str): path where JSON file shall be stored
    outFile(str): name of the resulting JSON file
    ''' 
    with open(path+outFile+'.json','w') as fp:
        json.dump(manifestDict,fp,indent=4)


def createManifestCombined_hourly(fileList, ncFileList, year, bucket_list, directory_manifest,directory_outfile):
    ''' Function that loops over a fileList and creates manifest files for ERA5 hourly assets.
    
    Parameters:
    fileList (list): List of file list of all variables that will be part of the EE asset
    ncFileList (list): list of NetCDF files in order to retrieve the time steps and be able to convert them to epoch times
    year(str): addition to outfile name
    bucket_list(list): list of GCP buckets holding files to be ingested to Earth Engine
    directory_manifest(str): path to example manifests
    directory_outfile(str): path where manifest files shall be stored
    ''' 
    for i in range(0,len(fileList[0])):
        print(len(fileList[0]))
        item = list(zip(*fileList))[i]

        tmp = re.findall('\d+', item[0])
    
        # Create assetName based on year month and day information
        assetName=tmp[3]+tmp[4]+tmp[5]
        
        # open a NetCDF file in order to retrieve the time stamps
        ncFile = gdal.Open(ncFileList[i])

        # Convert the time stamps to epoch times
        ls_epochtimes = getEpochTimes(ncFile,24)

        uris_list = []
        for i in item:
             tmp2 = i.split('/')
             uris_list.append(tmp2[4])
        print(uris_list)

        for k in range(0,len(ls_epochtimes)-1):
            print(k)
            hour= str(k).zfill(2)
            # For all 24 epoch times, create manifest
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
            # Save JSON object 
            manifestToJSON(manifest,directory_outfile+year+'/',outfile)


def createManifestCombined_daily(fileList, year,bucket_list, directory_manifest,directory_outfile):
    ''' Function that loops over a fileList and creates manifest files for ERA5 daily assets.
    
    Parameters:
    fileList (list): List of file list of all variables that will be part of the EE asset
    year(str): addition to outfile name
    bucket_list(list): list of GCP buckets holding files to be ingested to Earth Engine
    directory_manifest(str): path to example manifests
    directory_outfile(str): path where manifest files shall be stored
    ''' 
    for i in range(0,len(fileList[0])):
        item = list(zip(*fileList))[i]

        tmp = re.findall('\d+', item[0])
        assetName=tmp[3]+tmp[4]+tmp[5]
        
        # Get start and end times of the asset in epoch times
        ls_epochtimes = getEpochTimes_daily(int(tmp[3]),int(tmp[4]),int(tmp[5]))
        
        uris_list = []
        for i in item:
            tmp2 = i.split('/')
            uris_list.append(tmp2[4])
            
        # Update manifest information
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
        # Save JSON object
        manifestToJSON(manifest,directory_outfile+year+'/',outfile)
        manifestToJSON(manifest,directory_outfile+year+'/',outfile)


def createManifestCombined_monthly(fileList, year,bucket_list, directory_manifest,directory_outfile):
    ''' Function that loops over a fileList and creates manifest files for ERA5 monthly assets.
    
    Parameters:
    fileList (list): List of file list of all variables that will be part of the EE asset
    year(str): addition to outfile name
    bucket_list(list): list of GCP buckets holding files to be ingested to Earth Engine
    directory_manifest(str): path to example manifests
    directory_outfile(str): path where manifest files shall be stored
    ''' 
    for i in range(0,len(fileList[0])):

        item = list(zip(*fileList))[i]

        tmp = re.findall('\d+', item[0])
        assetName=tmp[3]+tmp[4]
        
        # Get start and end times of the asset in epoch times        
        ls_epochtimes = getEpochTimes_monthly(int(tmp[3]),int(tmp[4]))
        
        uris_list = []
        for i in item:
            tmp2 = i.split('/')
            print(tmp2)
            uris_list.append(tmp2[4])
            
        # Update manifest   
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
        # Save JSON object
        manifestToJSON(manifest,directory_outfile+year+'/',outfile)



################################################################################
# Functions to upload files to Google Cloud Platform (GCP)
################################################################################


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    ''' Function that uploads a file to Google Cloud Platform.
    
    Parameters:
    bucket_name(str): name of bucket on GCP
    source_file_name(str): name of local file to be uploaded
    destination_blob_name(str): name of file on GCP
    ''' 
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


def uploadMonthlyFilesToGCP(directory,parameter,year,bucket):
    ''' Function that uploads monthly files to Google Cloud Platform.
    
    Parameters:
    directory(str): path to directory with files to be uploaded
    parameter(str): parameter name - addition to source file name
    year(str): year - addition to source file name
    bucket(str): name of bucket on GCP
    ''' 
    fileList = createFileList(directory,'./era5_'+parameter+'/tiff/monthly/'+year+'/*.tif')
    fileList.sort()
    for file in fileList:
        tmp = file.split('/')
        print(tmp)
        destname = tmp[5]
        print(destname)
        upload_blob(bucket,file,destname)


def uploadToGCP(directory,year,time_step,parameter,bucket):
    ''' Function that uploads a file to Google Cloud Platform.
    
    Parameters:
    directory(str): path to directory with files to be uploaded
    year(str): year - addition to source file name
    time_step(str): time step - addition to source file name
    parameter(str): parameter name - addition to source file name
    bucket(str): name of bucket on GCP
    ''' 
    fileList = createFileList(directory, 'era5_'+parameter+'/tiff/'+time_step+'/'+year+'/*.tif')
    fileList.sort()

    for file in fileList:
        print(file)
        tmp = file.split('/')
        print(tmp)

        upload_blob(bucket,file,tmp[4])

################################################################################
# Function to call the command from the earthengine Python API to ingest files
# stored on GCP into Earth Engine with the help of manifest upload
################################################################################


def ee_ingest(manifest_list):
    ''' Function that calls the earthengine Python API command to ingest files stored on GCP into Earth Engine
    based on manifest upload.
    
    Parameters:
    mainfest_list(list): path to manifests to upload
    '''
    for i in manifest_list:
        print(i)
        cmd = 'earthengine --use_cloud_api upload image --force --manifest ' + i
        print(cmd)
        os.system(cmd)





