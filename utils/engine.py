import ee
import datetime
from utils.geojsonParser import Parser
import json

class Engine:
    def __init__(self):
        try:
            ee.Initialize()
        except ee.ee_exception.EEException:
            ee.Authenticate()
            ee.Initialize()
        print("Earth Engine initialized")

    def load_geojson(self, filename):
        self.parsedGeo = Parser(filename)
        self.parsedGeo.extractCoordinates()
        self.region = ee.Geometry.MultiPolygon(self.parsedGeo.coordinates)
    def satelliteDataType(self, imageCollection=None, dataType=None):
        ## Identify the Earth Engine Data Catalog
        ## imageCollection takes precedence over dataType definition
        ## Landsat 8 NDVI made from Tier 1 orthorectified scenes,
        ## using top-of-atmosphere (ToA) reflectance
        ## ToA details (https://www.sciencedirect.com/science/article/pii/S0034425709000169)

        if imageCollection:
            self.imageCollection = ee.ImageCollection(imageCollection)
        elif dataType.lower() == 'ndvi':
            imageCollection = "LANDSAT/LC08/C01/T1_8DAY_NDVI"
            self.imageCollection = ee.ImageCollection(imageCollection)
        else:
            print("There are no other data yet")

    def satelliteDataCalc(self, year):
        ## Calculate satellite data value (e.g. NDVI)
        ## filtered across quarter-yearly set for enhanced resolution.
        self.calcData = []
        for i in range(1, 12, 3):
            i_datetime = datetime.datetime.strptime(f'{i}-01-{year}', '%m-%d-%Y') # force date to 1st of each month
            e_month = i+2
            e_date = i_datetime + datetime.timedelta(e_month*365/12)
            e_datetime = datetime.datetime.strptime(f'{e_date.month}-01-{e_date.year}', '%m-%d-%Y') - datetime.timedelta(days=1)
            init_date = ee.Date(i_datetime)
            end_date = ee.Date(e_datetime)

            print("ImageCollection Reduction activating...")
            data = self.imageCollection \
                .filterDate(init_date, end_date) \
                .filterBounds(self.region) \
                .reduce(ee.Reducer.mean())
            print("Reduction complete!")
            output = data.toDictionary()
            
            # print(output.keys())

            # data = ee.Dictionary(
            #     {
            #         "image":data,
            #         "time":init_date
            #     }
            # )
            fname = datetime.datetime.strftime(i_datetime,'%Y-%b')
            print("Saving data")
            with open(f"data/{fname}.json", 'w+') as f:
                # json.dump(f, output.get('NDVI'))
                f.write(str(output.get('NDVI')))