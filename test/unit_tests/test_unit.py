#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os
import pandas as pd
import numpy as np
import xarray as xr
import unittest
import xradial.dataframe as dataframe
import xradial.utils as utils

class TestXRadials(unittest.TestCase):

    def setUp(self):

        # set test paths up
        test_root = os.path.dirname(os.path.dirname(__file__))
        self.codar_test_fp = os.path.join(
            test_root,
            "data/codar_ascii/RDL_m_Rutgers_AMAG_2018_02_14_0000.hfrss10lluv"
        )

        self.wera_test_fp = os.path.join(
            test_root,
            "data/wera_ascii/RDL_SC_GTN_2018_02_14_0023.hfrweralluv1.0"
        )
        

    def test_rb2ll(self):
        """Ensure numerical function to calculate latitude and longitude
        works as expected."""

        # TODO use numpy for floating point comparisons?

        lon0 = 88.4507
        lat0 = 62.3998
        r = 44
        b = 0.4

        out = utils._rb2ll(lon0, lat0, r, b)
        self.assertTrue(np.allclose(np.array(out), np.array([88.45671962753298, 62.794567620064484])))

        lon0 = 45.07
        lat0 = 39.98
        r = 27
        b = 5.6

        out = utils._rb2ll(lon0, lat0, r, b)
        self.assertTrue(np.allclose(np.array(out), np.array([45.10095433988366, 40.221998475529155])))

    def test_get_metadata(self):
        """Check that a dictionary of metadata information is returned, and the
        mappings are correct."""

        correct_codar_metadata = {
            'CTF': 1.0, 
            'FileType': 'LLUV rdls "RadialMap"', 
            'LLUVSpec': '1.26  2016 10 07', 
            'UUID': '379A036C-F505-43C5-AAA1-1CBE12739086', 
            'Manufacturer': 'CODAR Ocean Sensors. SeaSonde', 
            'Site': 'AMAG ""', 
            'TimeStamp': '2018 02 14  00 00 00', 
            'TimeZone': '"UTC" +0.000 0 "Atlantic/Reykjavik"', 
            'TimeCoverage': '180.000 Minutes', 
            'Origin': '40.9693333  -72.1237000', 
            'GreatCircle': '"WGS84" 6378137.000  298.257223562997', 
            'GeodVersion': '"CGEO" 1.70  2014 09 09', 
            'LLUVTrustData': 'all %% all lluv xyuv rbvd', 
            'RangeStart': 2, 
            'RangeEnd': 35, 
            'RangeResolutionKMeters': 5.8249, 
            'RangeCells': 49, 
            'DopplerCells': 1024, 
            'DopplerInterpolation': 2, 
            'AntennaBearing': '214.0 True', 
            'ReferenceBearing': '0 True', 
            'AngularResolution': '5 Deg', 
            'SpatialResolution': '5 Deg', 
            'PatternType': 'Measured', 
            'PatternDate': '2114 10 19  20 11 20', 
            'PatternResolution': '1.0 deg', 
            'PatternSmoothing': '10.0 deg', 
            'PatternUUID': 'BAA8BFBD-958A-49BC-943C-B9EC205BBAF1', 
            'TransmitCenterFreqMHz': 4.513, 
            'TransmitBandwidthKHz': -25.733913, 
            'TransmitSweepRateHz': 1.0, 
            'DopplerResolutionHzPerBin': 0.00048828099999999997, 
            'FirstOrderMethod': 0, 
            'BraggSmoothingPoints': 4, 
            'CurrentVelocityLimit': 100.0, 
            'BraggHasSecondOrder': 0, 
            'RadialBraggPeakDropOff': 100.0, 
            'RadialBraggPeakNull': 10.0, 
            'RadialBraggNoiseThreshold': 5.0, 
            'PatternAmplitudeCorrections': '0.1735  0.1822', 
            'PatternPhaseCorrections': '-170.00  -132.00', 
            'PatternAmplitudeCalculations': '0.0779  0.1947', 
            'PatternPhaseCalculations': '119.30  -124.70', 
            'RadialMusicParameters': '40.000 20.000 2.000', 
            'RadialMinimumMergePoints': 2, 
            'FirstOrderCalc': 1, 
            'MergeMethod': '1 MedianVectors', 
            'PatternMethod': '1 PatternVectors', 
            'MergedCount': 5, 
            'TableType': 'LLUV RDL9', 
            'TableColumns': 18, 
            'TableColumnTypes': 'LOND LATD VELU VELV VFLG ESPC ETMP MAXV MINV ERSC ERTC XDST YDST RNGE BEAR VELO HEAD SPRC', 
            'TableRows': 672, 
            'TableStart': np.nan
        }

        codar_metadata_out = utils.get_metadata_from_file(self.codar_test_fp)

        # non-numeric metadata
        self.assertEqual(
            codar_metadata_out['TableType'],
            correct_codar_metadata['TableType']
        )
        self.assertEqual(
            codar_metadata_out['PatternAmplitudeCorrections'],
            correct_codar_metadata['PatternAmplitudeCorrections']
        )
        self.assertEqual(
            codar_metadata_out['Origin'],
            correct_codar_metadata['Origin']
        )

        # TODO
        # numeric metadata
        # can't easily compare np.nan, just test a few
        codar_metadata_out = utils.get_metadata_from_file(self.codar_test_fp, numeric=True)
        self.assertEqual(type(codar_metadata_out['TableRows']), np.int64)
        self.assertEqual(
            codar_metadata_out['TableRows'],
            correct_codar_metadata['TableRows']
        )

        self.assertEqual(type(codar_metadata_out['TransmitBandwidthKHz']), np.float64)
        self.assertEqual(
            codar_metadata_out['TransmitBandwidthKHz'],
            correct_codar_metadata['TransmitBandwidthKHz']
        )

    def test_calc_max_range(self):
        metadata = { # metadata from test CODAR file, using pd.to_numeric
            'CTF': 1.0, 
            'FileType': 'LLUV rdls "RadialMap"', 
            'LLUVSpec': '1.26  2016 10 07', 
            'UUID': '379A036C-F505-43C5-AAA1-1CBE12739086', 
            'Manufacturer': 'CODAR Ocean Sensors. SeaSonde', 
            'Site': 'AMAG ""', 
            'TimeStamp': '2018 02 14  00 00 00', 
            'TimeZone': '"UTC" +0.000 0 "Atlantic/Reykjavik"', 
            'TimeCoverage': '180.000 Minutes', 
            'Origin': '40.9693333  -72.1237000', 
            'GreatCircle': '"WGS84" 6378137.000  298.257223562997', 
            'GeodVersion': '"CGEO" 1.70  2014 09 09', 
            'LLUVTrustData': 'all %% all lluv xyuv rbvd', 
            'RangeStart': 2, 
            'RangeEnd': 35, 
            'RangeResolutionKMeters': 5.8249, 
            'RangeCells': 49, 
            'DopplerCells': 1024, 
            'DopplerInterpolation': 2, 
            'AntennaBearing': '214.0 True', 
            'ReferenceBearing': '0 True', 
            'AngularResolution': '5 Deg', 
            'SpatialResolution': '5 Deg', 
            'PatternType': 'Measured', 
            'PatternDate': '2114 10 19  20 11 20', 
            'PatternResolution': '1.0 deg', 
            'PatternSmoothing': '10.0 deg', 
            'PatternUUID': 'BAA8BFBD-958A-49BC-943C-B9EC205BBAF1', 
            'TransmitCenterFreqMHz': 4.513, 
            'TransmitBandwidthKHz': -25.733913, 
            'TransmitSweepRateHz': 1.0, 
            'DopplerResolutionHzPerBin': 0.00048828099999999997, 
            'FirstOrderMethod': 0, 
            'BraggSmoothingPoints': 4, 
            'CurrentVelocityLimit': 100.0, 
            'BraggHasSecondOrder': 0, 
            'RadialBraggPeakDropOff': 100.0, 
            'RadialBraggPeakNull': 10.0, 
            'RadialBraggNoiseThreshold': 5.0, 
            'PatternAmplitudeCorrections': '0.1735  0.1822', 
            'PatternPhaseCorrections': '-170.00  -132.00', 
            'PatternAmplitudeCalculations': '0.0779  0.1947', 
            'PatternPhaseCalculations': '119.30  -124.70', 
            'RadialMusicParameters': '40.000 20.000 2.000', 
            'RadialMinimumMergePoints': 2, 
            'FirstOrderCalc': 1, 
            'MergeMethod': '1 MedianVectors', 
            'PatternMethod': '1 PatternVectors', 
            'MergedCount': 5, 
            'TableType': 'LLUV RDL9', 
            'TableColumns': 18, 
            'TableColumnTypes': 'LOND LATD VELU VELV VFLG ESPC ETMP MAXV MINV ERSC ERTC XDST YDST RNGE BEAR VELO HEAD SPRC', 
            'TableRows': 672, 
            'TableStart': np.nan
        }

        arr1 = np.array([utils.calc_max_range(metadata)])
        arr2 = np.array([443.1641923332595])
        self.assertTrue(np.allclose(arr1, arr2))

    def test_get_range_res_start_end(self):
        # metadata from test codar file used
        metadata = { # truncated, need only a few fields
            'RangeStart': 2, 
            'RangeEnd': 35, 
            'RangeResolutionKMeters': 5.8249,
        }

        rnge_s, rnge_e, rnge_res_km, rnge_res_m = utils.get_range_res_start_end(metadata)

        self.assertEqual(
            (rnge_s, rnge_e, rnge_res_km, rnge_res_m),
            (2, 35, 5.8249, None)
        )

        metadata = { # truncated, need only a few fields
            'RangeStart': 2, 
            'RangeEnd': 35, 
            'RangeResolutionMeters': 5000.8249,
        }

        rnge_s, rnge_e, rnge_res_km, rnge_res_m = utils.get_range_res_start_end(metadata)
        self.assertEqual(
            (rnge_s, rnge_e, rnge_res_km, rnge_res_m),
            (2, 35, None, 5000.8249)
        )

    def test_get_range_resolution_precision(self):
        range_resolution_kmeters = 5.8249
        range_resolution_meters = None

        self.assertEqual(
            utils.get_range_resolution_precision(
                range_resolution_kmeters,
                range_resolution_meters
            ),
            4
        )

        range_resolution_kmeters = None
        range_resolution_meters = 5000.8249

        self.assertEqual(
            utils.get_range_resolution_precision(
                range_resolution_kmeters,
                range_resolution_meters
            ),
            4
        )

    def test_create_time(self):
        metadata = { # truncated, only need a few fields
            'TimeStamp': '2018 02 14  00 00 00', 
        }
        dt = datetime.datetime(2018, 2, 14, 0, 0, 0)
        self.assertEqual(utils.create_time(metadata), dt)
        

    def test_create_initial_dataframe(self):
        # create metadata
        metadata = { # truncated, only need a few fields
            'TableColumnTypes': 'LOND LATD VELU VELV VFLG ESPC ETMP MAXV MINV ERSC ERTC XDST YDST RNGE BEAR VELO HEAD SPRC', 
            'TimeStamp': '2018 02 14  00 00 00', 
        }

        dt = datetime.datetime(2018, 2, 14, 0, 0, 0)
        TIME_VAR_STR = "time"
        df = dataframe.create_initial_dataframe(
            self.codar_test_fp, 
            metadata, 
            TIME_VAR_STR, 
            dt
        ) 

        correct_df = pd.read_csv(
            self.codar_test_fp,
            header=None, 
            sep=r'\s+', 
            comment='%', 
            encoding='ascii', 
            names=metadata['TableColumnTypes'].split()
        )
        correct_df[TIME_VAR_STR] = dt

        self.assertTrue(df.equals(correct_df))


    def test_get_range_cells(self):

        # create needed metadata
        metadata = { # truncated, only need a few fields
            'RangeResolutionKMeters': 5.8249, 
            'RangeCells': 49, 
            'TableColumnTypes': 'LOND LATD VELU VELV VFLG ESPC ETMP MAXV MINV ERSC ERTC XDST YDST RNGE BEAR VELO HEAD SPRC', 
        }

        range_res_km = 5.8249

        # create dataframe as it is created in the main function
        df = pd.read_csv(
            self.codar_test_fp,
            header=None, 
            sep=r'\s+', 
            comment='%', 
            encoding='ascii', 
            names=metadata['TableColumnTypes'].split()
        )

        # max range, as taken from above
        max_range = 500

        range_cells = utils.get_range_cells(metadata, df, max_range, range_res_km)
        self.assertEqual(range_cells, 49)

    def test_get_olat_olon(self):
        # CODAR metadata 
        metadata = {
            'Origin': '40.9693333  -72.1237000', 
        }

        olat, olon = utils.get_olat_olon(metadata)
        self.assertEqual(
            (olat, olon),
            (40.9693333, -72.1237000)
        )

    def test_get_angular_resolution(self):
        metadata = { # truncated CODAR metadata
            'AngularResolution': '5 Deg', 
        }

        ang_res = float(5)
        self.assertEqual(utils.get_angular_resolution(metadata), ang_res)

    def test_get_antenna_bearing(self):
        metadata = { 
            'AntennaBearing': '214.0 True',
        }

        ant_bear = 214.0
        self.assertEqual(
            utils.get_antenna_bearing(metadata),
            ant_bear
        )

    def test_reindex_df_by_lat_lon(self):
        
        # WERA metadata
        metadata = { # truncated, only need a few fields
            'TableColumnTypes': 'LOND LATD VELU VELV EVAR EACC XDST YDST RNGE BEAR VELO HEAD', 
        }

        olat, olon = (33.356111, -79.152778)
        max_range = 239.57834211787252
        dt = datetime.datetime(2018, 2, 14, 0, 23, 0)
        TIME_VAR_STR = "time"

        df = pd.read_csv(
            self.wera_test_fp,
            header=None, 
            sep=r'\s+', 
            comment='%', 
            encoding='ascii', 
            names=metadata['TableColumnTypes'].split()
        )
        df[TIME_VAR_STR] = dt

        df_out = dataframe.reindex_df_by_lat_lon(
            df, olat, 
            olon, 
            max_range, 
            TIME_VAR_STR, 
        )

        self.assertIsInstance(df_out.index, pd.MultiIndex)
        self.assertTrue(
            all(name in df_out.index.names for name in [TIME_VAR_STR, "i", "j"])
        )
        
    def test_reindex_df_by_range_bearing(self):
        # CODAR metadata
        olat, olon = (40.9693333, -72.1237000)
        max_range = 500
        dt = datetime.datetime(2018, 2, 14, 0, 0, 0)
        TIME_VAR_STR = "time"
        angular_res = 5.0
        range_cells = 49

        # resolutions
        range_resolution_kmeters = 5.8249
        range_resolution_kmeters_decimal_digits = 4

        # table column types
        TableColumnTypes = 'LOND LATD VELU VELV VFLG ESPC ETMP MAXV MINV ERSC ERTC XDST YDST RNGE BEAR VELO HEAD SPRC'

        df = pd.read_csv(
            self.codar_test_fp,
            header=None, 
            sep=r'\s+', 
            comment='%', 
            encoding='ascii', 
            names=TableColumnTypes.split()
        )
        df[TIME_VAR_STR] = dt

        df_out = dataframe.reindex_df_by_range_bearing(
            df,
            angular_res,
            range_resolution_kmeters_decimal_digits,
            range_resolution_kmeters,
            max_range, 
            range_cells,
            TIME_VAR_STR,
        )

        self.assertIsInstance(df_out.index, pd.MultiIndex)
        self.assertTrue(
            all(name in df_out.index.names for name in [TIME_VAR_STR, 'BEAR', 'RNGE'])
        )

if __name__ == "__main__":
    unittest.main()
