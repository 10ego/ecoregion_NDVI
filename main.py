from utils.engine import Engine

EE = Engine()

EE.load_geojson('data/F1_1_Perm_upland_streams.geojson')
EE.satelliteDataType(dataType="ndvi")
EE.satelliteDataCalc(2020)
