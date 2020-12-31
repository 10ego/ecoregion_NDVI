import ee
import json
import numpy as np
from datetime import datetime
from dateutil.relativedelta import *

import sqlite3

ee.Initialize()
print("Initializing Earth Engine..")

with open('ecoRegions.geojson') as f:
	print("Loading eco region shapefile..(this may take a few minutes)")
	ecoregions = json.load(f)
	print("Shapefile loaded.")

def define_region(geoJSON):	
	geometry = ee.FeatureCollection(
		[
			ee.Geometry(geoJSON) #Insert Polygon shape lists
		]
	)
	return ee.FeatureCollection(geometry)

modisNDVI = ee.ImageCollection("MODIS/MCD43A4_006_NDVI")

def define_date(start, end): #%Y-%m-%d datetime string format. e.g. 2020-12-02
	startDate = ee.Date(start) #start Month
	endDate = ee.Date(end) #end Month (do not go to last DATE as this will create a 13 month year cycle)
	nMonths = ee.Number(endDate.difference(startDate, 'month')).round()
	return startDate, nMonths

def feature_n(geometry, m, startDate):
	startDate = datetime.strptime(startDate, '%Y-%m-%d')
	sdate = (startDate + relativedelta(months=+m)).strftime('%Y-%m-%d')
	ini = ee.Date(sdate)
	n = m+1 #For calculating 2 months ahead, then back 1 day to get coverage of all dates in a month
	edate = (startDate + relativedelta(months=+n) + relativedelta(days=-1)).strftime('%Y-%m-%d')
	end = ee.Date(edate)
	region = define_region(geometry)
	data = modisNDVI.filterDate(ini,end).mean().reduceRegion(
		reducer = ee.Reducer.mean(),
		geometry = region.geometry(),
		scale = 1000,
		maxPixels = 10000000,
		bestEffort = True
	)
	return data.combine(ee.Dictionary({'time':ini}))

def feature_m(region, startDate):
	timeDict = map(lambda n:
		feature_n(region, n, startDate),
		np.arange(12)
	)
	return timeDict


# LOAD SHAPEFILE
with open('ecoRegions.geojson') as f:
	ecoregions = json.load(f)

ecoregions = [x for x in ecoregions['features'] if x['type']!='MultiPoint'] # Select the features which contains the multipolygon region data among other useful metadata
#year = input("Year:")
year = 2019
start_date = f"{year}-01-01"


def write_to_db(ecoregions, start_date):
	c=0
	for region in ecoregions:
		ndvis = feature_m(region['geometry'], start_date)
		c+=1
		print(f"Writing {c} region out of total {len(ecoregions)}..")	
		for ndvi in ndvis:
			n = ndvi.getInfo()
			yield (region['id'], n.get('NDVI'), n.get('time')['value'])	


iteration_ = input("Iteration starting position:")
iteration_ = int(iteration_)
ecoregions = ecoregions[iteration_:]
conn = sqlite3.connect('ndvi.db')
c = conn.cursor()
#c.executemany("INSERT INTO monthly_ndvi (region_id, ndvi, date) VALUES (?, ?, ?)", write_to_db(ecoregions, start_date))
counter = iteration_-1
for region in ecoregions:
	counter+=1
	month=0
	ndvis = feature_m(region['geometry'], start_date)
	for ndvi in ndvis:
		month+=1
		print(f"Processing month {month} for region {counter}.")
		try:
			n = ndvi.getInfo()
			c.execute("INSERT INTO monthly_ndvi (region_id, ndvi, date) VALUES (?, ?, ?)", (region['id'], n.get('NDVI'), n.get('time')['value']))
			conn.commit()
		except Exception as e:
			print(f"Failed to process month {month} for region {counter}.")
			with open('error.log', 'w+') as f:
				f.write(f"[{counter}] {e.args}. Failed at month {month} for region {region['id']}\n")
	print(f"Completed region {counter} out of total {len(ecoregions)}.")
conn.close()
