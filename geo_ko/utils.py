# -*- coding: utf-8 -*-
import logging
import tempfile
import tarfile, zipfile
import shutil

from fiona import collection

from shapely.geometry import asShape

from sqlalchemy import Column

from geoalchemy2 import Geometry, Geography
from geoalchemy2 import WKTElement

GEO_COLUMN_NAME = 'geom'

def populate_geo_table(table, data, mapping):
    tmp = tempfile.NamedTemporaryFile()
    tmp.file.write(data)
    tmp.file.flush()
    tmpdir = tempfile.mkdtemp()
    filenames = []
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
            with collection(tmpdir + '/' + filename) as source:
                dbf_mapping = {}
                for sk in source.schema['properties'].keys():
                    dbf_mapping[sk.lower()] = sk
                #the source column names extracted by pydbf are lowercase
                #fiona expects them to be mixed case
                for k, v in mapping.iteritems():
                    if v['name'] in dbf_mapping:
                        v['name'] = dbf_mapping[v['name']]
                for record in source:
                    insert = {}
                    for dest, src in mapping.iteritems():
                        if src['name'] in record['properties']:
                            insert[dest] = record['properties'][src['name']]
                    if GEO_COLUMN_NAME in table.c.keys():
                        insert[GEO_COLUMN_NAME] = WKTElement(asShape(record['geometry']).wkt)

                    table.insert().values(**insert).execute()

    shutil.rmtree(tmpdir)
    tmp.close()


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
            with collection(tmpdir + '/' + filename) as src:
                result['geometry'] = src.schema['geometry']
                result['bounds'] = src.bounds
                result['crs'] = src.crs
    shutil.rmtree(tmpdir)
    tmp.close()
    return result

def define_geo_column(col):
    name = col.dest_column_name
    dim = col.column_lenght
    return Column(name, Geography(srid=4326, dimension=dim))
