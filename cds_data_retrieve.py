#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 17:57:33 2019

@author: julia_wagemann
"""


#!/usr/bin/env python
import cdsapi
import os
import pandas as pd
c = cdsapi.Client()


os.chdir('/Volumes/G-DRIVE with Thunderbolt/era5_minimum_2m_temperature_since_previous_post_processing/')


def retrieve_func(day, month, year,parameter,filename):
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type':'reanalysis',
            'format':'netcdf',
            'variable':[
              parameter
            ],
            'year':[
                  year
            ],
            'month':[
                  month
            ],
            'day':[
                day
            ],
            'time':[
                '00:00','01:00','02:00',
                '03:00','04:00','05:00',
                '06:00','07:00','08:00',
                '09:00','10:00','11:00',
                '12:00','13:00','14:00',
                '15:00','16:00','17:00',
                '18:00','19:00','20:00',
                '21:00','22:00','23:00'
            ],
            'area':'90/-180/-90/179.75'
        },
        filename)


def getDataList(parameter):
    startDate = '1999-11-30'
    endDate = '2019-08-31'
    dataList = pd.date_range(startDate,endDate).tolist()
    df = pd.to_datetime(dataList)
    for i in df:
        print(i.year,i.month,i.day)
        filename = "era5_"+parameter+"_"+str(i.year)+"_"+str(i.month).zfill(2)+"_"+str(i.day).zfill(2)+".nc"
        retrieve_func(str(i.day).zfill(2), str(i.month).zfill(2), i.year, parameter,filename)


getDataList('minimum_2m_temperature_since_previous_post_processing')


