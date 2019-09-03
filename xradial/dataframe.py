#!/usr/local/python
"""
Module containing DataFrame-specific operations.
"""

import numpy as np
import pandas as pd
import xradial.utils as utils # helper functions

def create_dataframe(fp, tvar, dt, metadata):
    """Given a file path, create a pandas DataFrame of the ASCII data.

    Args:
        fp (file path object): file path to data
        tvar (str): time variable
        dt (datetime.datetime): date 
        metadata (dict): dict of metadata

    Returns:
        pandas.DataFrame"""

    # ASCII data as pandas DataFrame
    df = create_initial_dataframe(fp, metadata, tvar, dt)

    # TODO raise custom error?
    # check that we have actual coordinates in the file
    if np.all(np.isnan(df['LATD'])) and np.all(np.isnan(df['LOND'])):
        raise TypeError("All LATD and LOND values are NaN, unable to reindex")

    return df

def reindex_dataframe(df, metadata, tvar, olat, olon):
    """Re-index the DataFrame based on the prevailing coordinate system.

    Args:
        df (pandas.DataFrame): DataFrame to reindex
        metadata (dict): dict of metadata
        tvar (str): time variable
        dt (datetime.datetime): date in file

    Returns:
        pandas.DataFrame: re-indexed DataFrame"""

    # calculate maximum range 
    max_range = utils.calc_max_range(metadata)

    # reindex the DataFrame by prevailing grid structure
    if (df['LOND'].unique().size * df['LATD'].unique().size) < (df['BEAR'].unique().size * df['RNGE'].unique().size): # reindex by lat/lon
        df = reindex_df_by_lat_lon(
            df,
            olat,
            olon,
            max_range,
            tvar,
        )

    else: # by range and bearing
        # calculate angular resolution, range resolution, range cells 
        a_res = utils.get_angular_resolution(metadata)
        rnge_s, rnge_e, rres_km, rres_m = utils.get_range_res_start_end(metadata)
        rres_precision = utils.get_range_resolution_precision(rres_km, rres_m)
        rnge_cells = utils.get_range_cells(metadata, df, max_range, rres_km)

        df = reindex_df_by_range_bearing(
            df, 
            a_res,
            rres_precision,
            rres_km,
            max_range, 
            rnge_cells,
            tvar, 
        )

    return df

def create_initial_dataframe(path, metadata, time_var_str, time):
    """Use pandas to read in a file and create a DataFrame object.
    Set the column "TIME_VAR_STR" as `time`, a passed datetime object.

    Args:
        path (str): path to file
        metadata (dict): dict of metadata
        time_var_str (str): name of time variable
        time (datetime.datetime): time in file

    Returns:
        pandas.DataFrame: DataFrame of ASCII data"""

    # create dataframe as it is created in the main function
    df = pd.read_csv(
        path,
        header=None, 
        sep=r'\s+', 
        comment='%', 
        encoding='ascii', 
        names=metadata['TableColumnTypes'].split()
    )

    # create a column for the time data
    df[time_var_str] = time
    return df

def reindex_df_by_lat_lon(df, olat, olon, max_range, time_var_str):
    """Create a MultiIndex from the time, latitude and longitude values.

    Args:
        df (pandas.DataFrame): DataFrame to re-index
        olat (float/None): origin latidude
        olon (float/None): origin longitude
        max_range (int): maximum range of data

    Returns:
        pandas.DataFrame: re-indexed DataFrame"""

    # TODO look into modifying in-place for performance

    # get unique lats/lngs
    unique_lats = np.unique(df['LATD']).round(7)
    unique_lons = np.unique(df['LOND']).round(7)

    # get min diff of unique lats/lons
    min_lat_diff = np.min(np.diff(unique_lats))
    min_lon_diff = np.min(np.diff(unique_lons))

    calculated_lat_slot = [int(i) for i in list(np.floor((df['LATD']-np.min(unique_lats))/min_lat_diff))]
    calculated_lon_slot = [int(i) for i in list(np.floor((df['LOND']-np.min(unique_lons))/min_lon_diff))]
    
    # add new columns to existing dataframe
    df['j'] = calculated_lat_slot 
    df['i'] = calculated_lon_slot

    df = df.set_index([time_var_str, 'i', 'j'])

    # calcuate max lat/lng extents based on bearing & range to calcuate theoretical number of lat/lon slots
    _, min_lat = utils._rb2ll(olon,olat,max_range,180)
    _, max_lat = utils._rb2ll(olon,olat,max_range,0)
    min_lon, _ = utils._rb2ll(olon,olat,max_range,270)
    max_lon, _ = utils._rb2ll(olon,olat,max_range,90)

    theoretical_max_lat_slot = np.int(np.ceil((max_lat-np.min(unique_lats))/min_lat_diff))
    theoretical_max_lon_slot = np.int(np.ceil((max_lon-np.min(unique_lons))/min_lon_diff))

    lat_slots = np.arange(theoretical_max_lat_slot)
    lon_slots = np.arange(theoretical_max_lon_slot)

    # create new index using the time, lon, lat
    df = df.reindex(pd.MultiIndex.from_product([np.array([df.index[0][0]]), lon_slots, lat_slots], names=df.index.names))

    return df

def reindex_df_by_range_bearing(df, angular_res,
    rres_precision, rres_km,
    max_range, range_cells, time_var_str):
    """Reindex the DataFrame by creating a MultiIndex of ranges and bearings.

    Args:
        df pandas.DataFrame: DataFrame to re-index
        angular_res (float/None): angular resolution
        rres_precision (int): range resolution precision
        rres_km (float): range resolution (kilometers)
        max_range (float): maximum range of data
        range_cells (int): number of range cells in data
        time_var_str (str): name of time variable

    Returns:
        pandas.DataFrame: re-indexed DataFrame"""

    # TODO look into modifying in-place for performance
    # TODO should raise more explicit errors

    unique_bearing_diffs = np.diff(np.unique(df['BEAR']))

    df = df.set_index([time_var_str, 'BEAR', 'RNGE'])
    
    # deal with missing angular resolution metadata
    if not angular_res:
        angular_res = unique_bearing_diffs.min() # just pick the first one
    
    # ranges
    assert all((np.unique(np.diff(df.index.get_level_values('RNGE')).round(decimals=rres_precision)) // rres_km) % 1. == 0)
    _rmin = df.index.get_level_values('RNGE').unique().min() # min/max ranges we see
    _rmax = df.index.get_level_values('RNGE').unique().max()

    all_ranges = np.unique(np.concatenate((
        (np.arange(_rmin, 0,    -rres_km)[1:][::-1]),
        (np.arange(_rmin, _rmax, rres_km)), # dont include last element (fixed issue here)
        (np.arange(_rmax, max_range+0.01, rres_km))
    )).round(decimals=rres_precision)[:range_cells])

    # bearings
    assert all(unique_bearing_diffs % angular_res == 0)
    _bmin = df.index.get_level_values('BEAR').unique().min() # min/max bearings we see
    _bmax = df.index.get_level_values('BEAR').unique().max()
    

    all_bearings = np.unique(np.concatenate((
        (np.arange(_bmin, 0, -angular_res)[1:][::-1]),
        (np.arange(_bmin, _bmax, angular_res)),
        (np.arange(_bmax, 360.1, angular_res))
    )))

    # create new index using time, bearings, ranges
    df = df.reindex(pd.MultiIndex.from_product([np.array([df.index[0][0]]), all_bearings, all_ranges], names=df.index.names))

    return df
