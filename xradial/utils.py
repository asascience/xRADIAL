#!/usr/bin/python
"""
Module containing helper functions for calculations.
"""

from geopy.distance import geodesic
import datetime
import geopy
import itertools
import json
import numpy as np
import pandas as pd
from pathlib import Path
import xarray as xr

def _rb2ll(lon0, lat0, r, b):
    """Vincenty Distance function.
    :param float lon0, lat0, r(ange), b(earing)
    :return tuple (lon (float), lat (float))"""
    origin = geopy.Point(lat0, lon0) # define the origin using geopy
    d = geodesic(kilometers=r).destination(origin, b) # using vincenty distance to get lat/lon from range and bearing
    return d.longitude, d.latitude

def get_metadata_from_file(path, numeric=False):
    """Open an ASCII file and parse out its metadata from the header.
    :param str fp: file path
    :param bool numeric: convert fields to numeric data types if possible
    :return dict"""
    with open(path, 'r', encoding='utf-8', errors="replace") as f:
        comments = itertools.takewhile(lambda s: s.startswith('%'), f)
        comments = list(map(lambda l: l[1:].strip(), comments))
        if numeric: # attempt to convert to numeric types
            metadata = {}
            for c in comments:
                if not c.startswith('%'):
                    metadata_entry = list(map(str.strip, c.split(':')))
                    metadata[metadata_entry[0]] = pd.to_numeric(metadata_entry[1], errors='ignore')
        else: # non-numeric
            metadata = dict([tuple(map(str.strip, c.split(':'))) for c in comments if not c.startswith('%')])
        return metadata

def calc_max_range(metadata):
    """Latest implementation of calc_max_range, used with numeric metadata.
    Based on information in the metadata (if available), calculate the maximum
    range of the file.
    :param dict metadata"""

    max_range_arr = np.array([60, 125, 250, 500])

    if (not 'TransmitCenterFreqMHz' in metadata) and ('RangeEnd' in metadata) and ('RangeResolutionKMeters' in metadata):    
        max_calc_range = metadata['RangeEnd'] * metadata['RangeResolutionKMeters']
        next_range_indx = np.argwhere(max_range_arr > max_calc_range).min()
        max_range = max_range_arr[next_range_indx]
    elif ('TransmitCenterFreqMHz' in metadata):
        # NOTE
        # assumes TransmitCenterFreqMHz is numeric
        # what to do if not numeric?
        max_range = 2000. / metadata['TransmitCenterFreqMHz']
    else:
        max_range = max_range_arr.max()

    return max_range

def get_range_res_start_end(metadata):
    """Function to get the range start, end, and resolution in kilometers
    or meters from the metadata.
    :param dict metadata"""

    range_start = metadata.get('RangeStart', None)
    range_end = metadata.get('RangeEnd', None)
    range_resolution_kmeters = metadata.get('RangeResolutionKMeters', None)
    range_resolution_meters = metadata.get('RangeResolutionMeters', None)
    return (range_start, range_end, range_resolution_kmeters, range_resolution_meters)

def get_range_resolution_precision(range_resolution_kmeters, range_resolution_meters):
    """Get the precision of the range resolution by taking the length of resolution string
    split on the decimal.
    :param str range_resolution_kmeters, range_resolution_meters
    :return int rres_precision"""

    # TODO add else? raise Exception?
    if range_resolution_kmeters:
        return len(str(range_resolution_kmeters).split('.')[-1])
    elif range_resolution_meters:
        return len(str(range_resolution_meters).split('.')[-1])

def create_time(metadata):
    """From information in the metadata dict, create a datetime object.
    :param dict metadata
    :return datetime.datetime"""

    return datetime.datetime(*list(map(int, metadata['TimeStamp'].split())))

def get_range_cells(metadata, df, _max_range, range_resolution_kmeters):
    """Return the number of range cells if present in the metadata. If not,
    calculate them based on the calculated maximum range and range resolution in
    kilometers.
    :param dict metadata
    :param pandas.Dataframe df
    :param int _max_range
    :param float range_resolution_kmeters"""

    # NOTE this assumes that range_resolution_kmeters is present
    range_cells = metadata['RangeCells'] if 'RangeCells' in metadata else None
    if range_cells:
        # ensure we have more than one unique value before attempting to use isclose
        if len((df['RNGE']/df['SPRC']).unique()) > 1:
            # TODO raise a better exception
            assert np.isclose(*(df['RNGE']/df['SPRC']).unique()) # verify RNGE/SPRC == range_resolution_kmeters everywhere
    else:
        range_cells = int(np.ceil(_max_range/range_resolution_kmeters))

    return range_cells

def get_olat_olon(metadata):
    """Get the origin latitude and longitude values from the metadata and
    convert to floats.
    :param dict metadata
    :return tuple of floats, length 2"""

    return list(map(float, metadata['Origin'].split())) if 'Origin' in metadata else (None, None)

def get_angular_resolution(metadata):
    """Get angular resolution from the metadata.
    :param dict metadata
    :return tuple of floats or None, legnth 2"""
    return float(metadata['AngularResolution'].split()[0]) if 'AngularResolution' in metadata else None # assumes 'X Deg'

def get_antenna_bearing(metadata):
    """Get the antenna bearing from the metadata and convert to float.
    :param dict metadata
    :return float"""

    return float(metadata['AntennaBearing'].split()[0]) if 'AntennaBearing' in metadata else None
