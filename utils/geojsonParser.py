import json

class Parser:
## GeoJSON parser  based on the GeoJSON Specification (RFC 7946) - 
## https://datatracker.ietf.org/doc/html/rfc7946
## Only handles small subset of curated types with the
## remaining types to be added only as needed or time permits.

    def __init__(self, filename):
        with open(filename) as f:
            self.geojson = json.load(f)
            self.geojson_type = self.geojson["type"]
            self.coordinates = []

    def extractCoordinates(self, geojson_type = None, geojson = None):
        ## Examines the geojson type and recursively extracts all coordinates.
        ## Note: CRS object is not supported!
        if geojson_type is None and geojson is None:
            geojson_type = self.geojson_type
            geojson = self.geojson
        if geojson_type == "FeatureCollection":
            geojson = geojson["features"]
            for g in geojson:
                self.extract_coordinates(geojson_type = g["type"], geojson = g)
        elif geojson_type == "GeometryCollection":
            geojson = geojson["geometries"]
        elif geojson_type == "Feature":
            geojson = [geojson["geometry"]]
        else:
            geojson == [geojson]

        for g in geojson:
            if (
                g["type"] == "Point" or
                g["type"] == "MultiPoint" or
                g["type"] == "LineString" or 
                g["type"] == "MultiLineString" or 
                g["type"] == "Polygon" or 
                g["type"] == "MultiPolygon"
            ):
                self.coordinates.append(g["coordinates"])
            
            else:
                raise GeoJSONTypeError("Not a valid GeoJSON Object type.")