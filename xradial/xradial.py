#!/usr/bin/python

import numpy as np
import os
import xradial.dataframe # dataframe operations
import xradial.utils
import xarray as xr

def create_xarray_dataset(fp, time_var_str, cf_time_units, numerical_metadata=False):
    """High-level wrapper for the xRADIAL API. Given a path to data, a name of the
    time variable, and a string of the CF-compliant time units, convert that ASCII
    data to an xarray Dataset object.
    :param file-path object fp    : file path to ASCII data
    :param str time_var_str       : name of time variable
    :param str cf_time_units      : string describing the units of the time variable
    :param bool numerical_metadata: indicator to convert metadata to numeric types"""

    # TODO move this out? specify in JSON maybe for extensibility?
    ColLongNameMap = {
        'TIME': 'time',
        'LOND': 'Longitude (deg)',
        'LATD': 'Latitude (deg)',
        'VELU': 'U comp (cm/s)',
        'VELV': 'V comp (cm/s)',
        'VFLG': 'VectorFlag (GridCode)',
        'ESPC': 'Spatial Quality',
        'ETMP': 'Temporal Quality',
        'MAXV': 'Velocity Maximum',
        'MINV': 'Velocity Minimum',
        'ERSC': 'Spatial Count',
        'ERTC': 'Temporal Count',
        'XDST': 'X Distance (km)',
        'YDST': 'Y Distance (km)',
        'RNGE': 'Range (km)',
        'BEAR': 'Bearing (True)',
        'VELO': 'Velocity (cm/s)',
        'HEAD': 'Direction (True)',
        'SPRC': 'Spectra RngCell',
        'OLAT': 'Origin Latitude',
        'OLON': 'Origin Longitude',
        'OLON': 'Origin Longitude',
        'ANTB': 'Antenna Bearing',
    }

    # get metadata from file
    metadata = xradial.utils.get_metadata_from_file(fp, numerical_metadata)

    # create datetime object used
    dt = xradial.utils.create_time(metadata)

    # calculate origin latitude and longitude; these are needed as 1-D later
    olat, olon = xradial.utils.get_olat_olon(metadata)

    # calculate antenna bearing; needed as 1-D later
    antenna_bearing = xradial.utils.get_antenna_bearing(metadata)

    # use pandas to read the ASCII file and create dataframe
    df = xradial.dataframe.create_dataframe(fp, time_var_str, dt, metadata)

    # reindex dataframe by prevailing coordinate system
    df = xradial.dataframe.reindex_dataframe(df, metadata, time_var_str, olat, olon)

    # convert dataframe to xarray object
    ds = xr.Dataset.from_dataframe(df)

    # add olat, olon, antenna_bearing to Dataset, time as only dimension
    ds['OLAT'] = ([time_var_str], [olat])
    ds['OLON'] = ([time_var_str], [olon])
    ds['ANTB'] = ([time_var_str], [antenna_bearing])

    # add metadata to Dataset
    ds.attrs = metadata

    # update time encoding
    ds[time_var_str].encoding.update({'dtype': 'float64', 'units': cf_time_units})
    
    # add variable long_name attributes from col_long_name_map
    for k,v in ColLongNameMap.items():
        if k in ds:
            ds[k].attrs.update({'long_name': v})

    return  ds
