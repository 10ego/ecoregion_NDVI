# Generating NDVI per ecoregion using Google Earth Engine

Google Earth Engine API serves a variety of satellite datasets including those from LANDSAT and MODIS.
Here is an example of using the MODIS NDVI dataset, calculating the average NDVI value given a certain shapefile data in the form of geoJSON.

## Shapefile
[The RESOLVE Ecoregions 2017 dataset](https://developers.google.com/earth-engine/datasets/catalog/RESOLVE_ECOREGIONS_2017?hl=en) was used to generate the shapefile.  It includes over 1100 regions in various forms including polygons, multipolygons, and multigeometry types.
A sample of the dataset is included in this repository.

## Interacting with Google Earth Engine

To use the [Google Earth Engine](https://signup.earthengine.google.com/) platform, an authenticated Google account is required.  The API library is available in both JavaScript and Python (there is a lack of documentation for pythonbut the function syntax remains similar enough).
It takes a very long time to complete the transaction between Earth Engine API request sent and response received.

## Calculating NDVI

Using the ecoregion geoJSON data, the script attempts to iterate over each region's geoJSON data and calculate the average NDVI value within the complex geometry shape.  To help reduce computational overload, the region's scales are approximated to 1km resolution with 10 million pixels per region as its maximum threshold. The data is averaged across a period of 1 month.
The received data is cleaned up and stored in a SQLite3 database.

## Future plans

The particular [MODIS dataset used] (https://developers.google.com/earth-engine/datasets/catalog/MODIS_MCD43A4_006_NDVI?hl=en) is generated from the composite data across 16-day cycle. The frequency of NDVI generated per month is arbitrarily determined and is an area of greater refinement.

A simple database was chosen with the sole purpose of recording the data and further alignment work remains for integration with the XAlgo rule systems..
