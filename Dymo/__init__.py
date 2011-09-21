from gzip import GzipFile
from csv import DictReader
from os.path import splitext
from re import compile

from ModestMaps.Geo import Location
from ModestMaps.OpenStreetMap import Provider
from ModestMaps.Core import Point, Coordinate

from .places import Place

_osm = Provider()

int_pat = compile(r'^-?\d{1,9}$') # up to nine so we don't cross 2^32
float_pat = compile(r'^-?\d+(\.\d+)?$')

def location_point(lat, lon, zoom):
    """ Return a point that maps to pixels at the requested zoom level for 2^8 tile size.
    """
    try:
        location = Location(float(lat), float(lon))
        coord = _osm.locationCoordinate(location).zoomTo(zoom + 8)
        point = Point(coord.column, coord.row)
        
        return location, point

    except ValueError:
        raise Exception((lat, lon, zoom))

def label_bbox(shape, zoom):
    """ Return an envelope in geographic coordinates based on a shape in pixels at a known zoom level.
    """
    pass

def point_lonlat(x, y, zoom):
    """ Return a longitude, latitude tuple from pixels at the requested zoom level.
    """
    try:
        coord = Coordinate(y, x, zoom + 8)
        location = _osm.coordinateLocation(coord)
        
        return location.lon, location.lat

    except ValueError:
        raise Exception((x, y, zoom))

def load_places(input_files, zoom):
    """
    """
    for input_file in input_files:
        name, ext = splitext(input_file)
    
        if ext == '.gz':
            input = GzipFile(input_file, 'r')
            input_file = name
        else:
            input = open(input_file, 'r')
    
        name, ext = splitext(input_file)
        
        if ext == '.csv':
            dialect = 'excel'
        elif ext in ('.tsv', '.txt'):
            dialect = 'excel-tab'
        
        rows = list(DictReader(input, dialect=dialect))
        types = dict()
        
        for row in rows:
            for (key, value) in row.items():
                if int_pat.match(value):
                    if key not in types:
                        types[key] = int
                elif float_pat.match(value):
                    if key not in types:
                        types[key] = float
                else:
                    types[key] = unicode
        
        for row in rows:
            name = row['name'].decode('utf-8')
            radius = int(row.get('point size', 8))
            
            fontsize = int(row.get('font size', 12))
            fontfile = row.get('font file', 'fonts/DejaVuSans.ttf')
            
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            location, point = location_point(lat, lon, zoom)
            
            properties = dict([(key, types[key](value)) for (key, value) in row.items()
                               if key not in ('latitude', 'longitude')])
            
            yield Place(name, fontfile, fontsize, location, point, radius, properties)
