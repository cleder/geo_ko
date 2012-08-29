from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='geo_ko',
      version=version,
      description="GeoAlchemy enabled Kotti",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='GIS Spatial GeoAlchemy Pyramid Kotti',
      author='Christian Ledermann',
      author_email='christian.ledermann@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'kotti_rdbt',
          'Fiona',
          'GeoAlchemy',
          'fastkml',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
