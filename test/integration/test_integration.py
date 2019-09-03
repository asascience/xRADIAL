#!/usr/bin/python

import numpy as np
import xarray as xr
import xradial.xradial as xradial
import os
import unittest

class TestxRADIALIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up data paths"""
        test_root = os.path.dirname(os.path.dirname(__file__))
        cls.codar_data = os.path.join(
            test_root,
            "data/codar_ascii/RDL_m_Rutgers_AMAG_2018_02_14_0000.hfrss10lluv"
        )

        cls.wera_data = os.path.join(
            test_root,
            "data/wera_ascii/RDL_SC_GTN_2018_02_14_0023.hfrweralluv1.0"
        )

    def test_create_xarray_dataset(self):
        time_var = "time"
        cf_time_units = "seconds since 1970-01-01 00:00:00"

        # Dataset with numeric metadata
        ds_codar = xradial.create_xarray_dataset(
            self.codar_data,
            time_var,
            cf_time_units,
            True
        )

        correct_metadata = dict([
            ('CTF', 1.0),
            ('FileType', 'LLUV rdls "RadialMap"'),
            ('LLUVSpec', '1.26  2016 10 07'),
            ('UUID', '379A036C-F505-43C5-AAA1-1CBE12739086'),
            ('Manufacturer', 'CODAR Ocean Sensors. SeaSonde'),
            ('Site', 'AMAG ""'),
            ('TimeStamp', '2018 02 14  00 00 00'),
            ('TimeZone', '"UTC" +0.000 0 "Atlantic/Reykjavik"'),
            ('TimeCoverage', '180.000 Minutes'),
            ('Origin', '40.9693333  -72.1237000'),
            ('GreatCircle', '"WGS84" 6378137.000  298.257223562997'),
            ('GeodVersion', '"CGEO" 1.70  2014 09 09'),
            ('LLUVTrustData', 'all %% all lluv xyuv rbvd'),
            ('RangeStart', 2),
            ('RangeEnd', 35),
            ('RangeResolutionKMeters', 5.8249),
            ('RangeCells', 49),
            ('DopplerCells', 1024),
            ('DopplerInterpolation', 2),
            ('AntennaBearing', '214.0 True'),
            ('ReferenceBearing', '0 True'),
            ('AngularResolution', '5 Deg'),
            ('SpatialResolution', '5 Deg'),
            ('PatternType', 'Measured'),
            ('PatternDate', '2114 10 19  20 11 20'),
            ('PatternResolution', '1.0 deg'),
            ('PatternSmoothing', '10.0 deg'),
            ('PatternUUID', 'BAA8BFBD-958A-49BC-943C-B9EC205BBAF1'),
            ('TransmitCenterFreqMHz', 4.513),
            ('TransmitBandwidthKHz', -25.733913),
            ('TransmitSweepRateHz', 1.0),
            ('DopplerResolutionHzPerBin', 0.00048828099999999997),
            ('FirstOrderMethod', 0),
            ('BraggSmoothingPoints', 4),
            ('CurrentVelocityLimit', 100.0),
            ('BraggHasSecondOrder', 0),
            ('RadialBraggPeakDropOff', 100.0),
            ('RadialBraggPeakNull', 10.0),
            ('RadialBraggNoiseThreshold', 5.0),
            ('PatternAmplitudeCorrections', '0.1735  0.1822'),
            ('PatternPhaseCorrections', '-170.00  -132.00'),
            ('PatternAmplitudeCalculations', '0.0779  0.1947'),
            ('PatternPhaseCalculations', '119.30  -124.70'),
            ('RadialMusicParameters', '40.000 20.000 2.000'),
            ('RadialMinimumMergePoints', 2),
            ('FirstOrderCalc', 1),
            ('MergeMethod', '1 MedianVectors'),
            ('PatternMethod', '1 PatternVectors'),
            ('MergedCount', 5),
            ('TableType', 'LLUV RDL9'),
            ('TableColumns', 18),
            ('TableColumnTypes', 'LOND LATD VELU VELV VFLG ESPC ETMP MAXV MINV ERSC ERTC XDST YDST RNGE BEAR VELO HEAD SPRC'),
            ('TableRows', 672),
            ('TableStart', np.nan)
        ])

        # metadata
        # can't compare nans using conventional assert on whole dict, just test a few equalities
        self.assertEqual(correct_metadata['CTF'], ds_codar.attrs['CTF'])
        self.assertTrue(np.allclose(np.array([correct_metadata['DopplerResolutionHzPerBin']]), np.array([ds_codar.attrs['DopplerResolutionHzPerBin']])))
        self.assertTrue(np.allclose(np.array([correct_metadata['CurrentVelocityLimit']]), np.array([ds_codar.attrs['CurrentVelocityLimit']])))
        self.assertTrue(np.allclose(np.array([correct_metadata['TableStart']]), np.array([ds_codar.attrs['TableStart']]), equal_nan=True))

        # string comparisons
        self.assertEqual(correct_metadata['TableColumnTypes'], ds_codar.attrs['TableColumnTypes'])

if __name__ == "__main__":
    unittest.main()
