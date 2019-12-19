# ERA5 reanalysis data in Google Earth Engine


This repository contains a set of functions and example scripts to ingest Copernicus ERA5 reanalysis data into Google Earth Engine based on [manifest uploads](https://developers.google.com/earth-engine/image_manifest).

The functions have been developed during the process of making a subset of the ERA5 reanalysis data available in Google Earth Engine. 

<br>

## Workflow overview
The workflow consists of six major steps:
  1.  Downloading hourly data as daily files or monthly aggregates in `NetCDF` format from the [Climate Data Store](https://cds.climate.copernicus.eu/#!/home) [`cdsapi`](https://pypi.org/project/cdsapi/)
  2.  Aggregating hourly files to daily means or sums (total precipitation) [`xarray`](http://xarray.pydata.org/en/stable/)
  3.  Converting `NetCDF` data files to `GeoTiff` [`gdal`](https://pypi.org/project/GDAL/)
  4.  Uploading hourly, daily and monthly `GeoTiff` files to [Google Cloud Platform (GCP)](https://cloud.google.com/)[`google-cloud-storage Python API`](https://cloud.google.com/storage/docs/reference/libraries)
  5.  Creating image manifests (JSON-based files) describing the metadata and band names of the resulting Earth Engine asset
  6.  Ingesting data files uploaded to GCP as assets into [Earth Engine](https://earthengine.google.com/) with the help of [`earthengine-api`](https://developers.google.com/earth-engine/python_install-conda.html) and [manifest uploads](https://developers.google.com/earth-engine/image_manifest)

<br>

![](/img/workflow.png)

<br>


## Repository content
TODO

## Python packages required
- [cdsapi](https://pypi.org/project/cdsapi/)
- [EarthEngine Python API](https://developers.google.com/earth-engine/python_install-conda.html)
- [google-cloud-storage Python API](https://cloud.google.com/storage/docs/reference/libraries)
- [gdal](https://pypi.org/project/GDAL/)
- [xarray](http://xarray.pydata.org/en/stable/)


## References
- [ERA5 reanalysis data in the Climate Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview)
- [Google Earth Engine](https://earthengine.google.com/)
- [ERA5 DAILY | GEE Public Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_DAILY)
- [ERA5 MONTHLY | GEE Pubic Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_MONTHLY)
- [ERA5 in GEE | Slides from the EarthEngineVirtualMeetup in Dec 2019](https://speakerdeck.com/jwagemann/era5-climate-reanalysis-in-earth-engine)


## License
<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.



