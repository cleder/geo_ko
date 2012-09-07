# -*- coding: utf-8 -*-
import logging
import geojson

logger = logging.getLogger('geo_ko')

from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy import asc, desc
from sqlalchemy import Table
# Column Types
from sqlalchemy import Boolean
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode

from sqlalchemy.exc import NoSuchTableError, InvalidRequestError

from geoalchemy2 import Geometry, Geography

from pyramid.response import Response

from kotti import DBSession
from kotti import metadata

from kotti_rdbt.resources import RDBTable
from kotti_rdbt.utils import define_table_columnns

def view_rdbtable_json(context, request):
    form = request.params
    limit = int(form.get('rp', 15))
    page = int(form.get('page', 1))
    start = max(0, (page - 1) * limit)
    sortorder = form.get('sortorder',None)
    sortname = form.get('sortname',None)
    sort = None
    searchfor = form.get('query',None)
    searchcol = form.get('qtype',None)
    search = None
    selects = []
    result = []
    try:
        columns, is_spatial = define_table_columnns(context)
        try:
            my_table = Table(context.table_name, metadata,
                *columns,  autoload=True)
        except InvalidRequestError:
            my_table = Table(context.table_name, metadata, autoload=True)
        tablen = my_table.count().execute()
        cols =[]
        for item in my_table.columns.items():
            if type(item[1].type) in [Boolean, Date,
                                DateTime, Integer, Unicode]:
                cols.append(item[0])
                selects.append( my_table.c.get(item[0]))
            if type(item[1].type) in [Geometry, Geography]:
                selects.append(func.ST_AsGeoJSON( my_table.c.get(item[0])))
                pass
        pk = my_table.primary_key
        if searchcol and searchfor:
            if my_table.columns.get(searchcol) is not None:
                search = my_table.columns.get(searchcol) == searchfor
        query = select(selects, search)
        rp = query.execute()
        for row in rp:
            properties ={}
            ids = []
            for c in cols:
                properties[c] = row[c]
            for c in rp.keys():
                if c not in cols:
                     geometry= geojson.loads(row[c])
            id = ':'.join(str(ids))
            result.append(
                geojson.Feature(
                    id=id,
                    geometry=geometry,
                    properties=properties))
        return Response(geojson.dumps(geojson.FeatureCollection(result)))
    except NoSuchTableError:
        return Response('[]')


def includeme_view(config):

    config.add_view(
        view_rdbtable_json,
        context=RDBTable,
        name='geojson',
        permission='view',
        )

def includeme(config):
    includeme_view(config)
