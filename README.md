# ERA5 reanalysis data in Google Earth Engine


This repository contains a set of functions and example scripts to ingest Copernicus ERA5 reanalysis data into Google Earth Engine based on [manifest uploads](https://developers.google.com/earth-engine/image_manifest).

The functions were developed during the process of making a subset of the ERA5 reanalysis data available in Google Earth Engine. 

<br>

## Workflow overview
The workflow consists of six major steps:
  1.  Downloading hourly data as daily files or monthly aggregates in `NetCDF` format from the [Climate Data Store](https://cds.climate.copernicus.eu/#!/home) with [`cdsapi`](https://pypi.org/project/cdsapi/)
  2.  Aggregating hourly files to daily means or sums (total precipitation) with [`xarray`](http://xarray.pydata.org/en/stable/)
  3.  Converting `NetCDF` data files to `GeoTiff` with [`gdal`](https://pypi.org/project/GDAL/)
  4.  Uploading hourly, daily and monthly `GeoTiff` files to [Google Cloud Platform (GCP)](https://cloud.google.com/) with [`google-cloud-storage Python API`](https://cloud.google.com/storage/docs/reference/libraries)
  5.  Creating image manifests (JSON-based files) describing the metadata and band names of the resulting Earth Engine asset
  6.  Ingesting data files uploaded to GCP as assets into [Earth Engine](https://earthengine.google.com/) with [`earthengine-api`](https://developers.google.com/earth-engine/python_install-conda.html) and [manifest uploads](https://developers.google.com/earth-engine/image_manifest)

<br>

![](/img/workflow.png)

<br>


## Repository content
* ERA5 in GEE functions
  * [Python script](./era5_in_gee_functions.ipynb) 
  * [Jupyter notebook](./era5_in_gee_functions.ipynb)
* Example workflows
  * [Hourly assets](./hourly_files_script.py)
  * [Daily assets](./daily_files_script.py)
  * [Daily single asset](./daily_files_script_single_parameter.py)
  * [Monthly assets](./monthly_files_script.py)
* Example manifest files
  * [Hourly multiple assets](./manifest_structure_hourly.json)
  * [Daily multiple assets](./manifest_structure_daily.json)
  * [Daily single asset](./manifest_structure_daily_single_parameter.json) 
  * [Monthly multiple assets](./manifest_structure_monthly.json)
 * Example scripts for
   * [Retrieve ERA5 reanalysis from the CDS with `cdsapi`](./cds_data_retrieve.py)
   * [Delete blobs from GCP buckets](./delete_from_gcp.py)

<br>

## Python packages required
- [cdsapi](https://pypi.org/project/cdsapi/)
- [EarthEngine Python API](https://developers.google.com/earth-engine/python_install-conda.html)
- [google-cloud-storage Python API](https://cloud.google.com/storage/docs/reference/libraries)
- [gdal](https://pypi.org/project/GDAL/)
- [xarray](http://xarray.pydata.org/en/stable/)

<br>

## Naming convention and folder structure
The scripts base on the following `naming convention` and `folder_structure`:
### naming convention
Data is downloaded from the Climate Data Store with the following syntax: 
* `era5_` + `name_of_variable_` + `year_` + `month_` + `day` + `.nc`
  * Example for a  file of 2m dewpoint temperature from 1 January 1980: `era5_2m_dewpoint_temperature_1980_01_01.nc`

### folder structure: 
(*example for 2m air temperature*)
- `era5_t2m`
  - `nc`
    - `hourly`
      - `year` (e.g. 1979)
    - `daily`
      - `year` (e.g. 1979)
    - `monthly`
      - `year` (e.g. 1979)
  - `tiff`
    - `hourly`
      - `year` (e.g. 1979)
    - `daily`
      - `year` (e.g. 1979)
    - `monthly`
      - `year` (e.g. 1979)
- `manifests`
  - `era5_hourly`
      - `year` (e.g. 1979)
  - `era5_daily`
      - `year` (e.g. 1979)
  - `era5_monthly`
      - `year` (e.g. 1979)
  - `manifest_template.json`


## References
- [ERA5 reanalysis data in the Climate Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview)
- [Google Earth Engine](https://earthengine.google.com/)
- [ERA5 DAILY | GEE Public Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_DAILY)
- [ERA5 MONTHLY | GEE Public Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_MONTHLY)
- [ERA5 in GEE | Slides from the EarthEngineVirtualMeetup in Dec 2019](https://speakerdeck.com/jwagemann/era5-climate-reanalysis-in-earth-engine)
- [ERA5 reanalysis data available in Earth Engine - ECMWF Newsletter Number 162 Winter 2020](https://www.ecmwf.int/en/newsletter/162/news/era5-reanalysis-data-available-earth-engine)

<br>

## License
<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.



