# -*- coding: utf-8 -*-
import logging
import tempfile
import tarfile, zipfile
import shutil

from fiona import collection

from geoalchemy import GeometryColumn, GeometryExtensionColumn
from geoalchemy import Geometry, Point, LineString, Polygon

GEO_COLUMN_NAME = 'geom'


def extract_geometry_info(data):
    tmp = tempfile.NamedTemporaryFile()
    tmp.file.write(data)
    tmp.file.flush()
    tmpdir = tempfile.mkdtemp()
    filenames = []
    result = {'name': GEO_COLUMN_NAME,
            'crs': None,
            'bounds': (-180.0, -90.0, 180.0, 90.0),
            'geometry': None}
    if tarfile.is_tarfile(tmp.name):
        tmptf = tarfile.open(tmp.name)
        for ti in tmptf.getmembers():
            if ti.isfile() and ti.size > 0 :
                tf = tmptf.extractfile(ti)
                import ipdb; ipdb.set_trace()
                tf.close()
        tmptf.close()
    elif zipfile.is_zipfile(tmp.name):
        tmpzip = zipfile.ZipFile(tmp.file)
        for zi in tmpzip.infolist():
            tz = tmpzip.open(zi)
            filenames.append(zi.filename)
            tf = open(tmpdir + '/' + zi.filename, 'w')
            tf.write(tz.read())
            tf.close()
            tz.close()
    for filename in filenames:
        if filename.endswith('.shp'):
            with collection(tmpdir + '/' + filename) as coll:
                result['geometry'] = coll.schema['geometry']
                result['bounds'] = coll.bounds
                result['crs'] = coll.crs
    shutil.rmtree(tmpdir)
    tmp.close()
    return result

def define_geo_column(col):
    name = col.dest_column_name
    dim = col.column_lenght
    if col.column_type == 'Point':
         return GeometryExtensionColumn(name, Geometry(dim))
    elif col.column_type == 'LineString':
         return GeometryExtensionColumn(name, Geometry(dim))
    elif col.column_type == 'Polygon':
         return GeometryExtensionColumn(name, Geometry(dim))
    else:
        raise NotImplementedError

