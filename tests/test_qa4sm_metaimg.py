# -*- coding: utf-8 -*-

from src.qa4sm_reader.meta_img import QA4SM_MetaImg
import os
import re
import numpy as np
import unittest
from src.qa4sm_reader import globals


class TestQA4SMMetaImgBasicIntercomp(unittest.TestCase):

    def setUp(self) -> None:
        self.testfile = '3-ERA5_LAND.swvl1_with_1-C3S.sm_with_2-SMOS.Soil_Moisture.nc'
        self.testfile_path = os.path.join(os.path.dirname(__file__), '..','tests',
                                          'test_data', self.testfile)
        self.img = QA4SM_MetaImg(self.testfile_path)

        self.n_ds = len(self.testfile.split('_with_'))

    def test_num2short2num(self):
        for num in range(self.n_ds):
            should_short = self.img.global_meta['val_dc_dataset{}'.format(num)]
            assert self.img._num2short(num) == should_short
            assert self.img._short2num(should_short) == num

    def test_short_names(self):
        # get short names from file
        ref_short_name, ds_short_names = self.img.get_short_names()
        ds_short_names = sorted(ds_short_names)
        assert ref_short_name == 'ERA5_LAND'
        assert 'SMOS' in ds_short_names
        assert 'C3S' in ds_short_names

        # short 2 pretty from file
        pty_ref, ref_vers, ref_vers_pty = self.img.short_to_pretty(ref_short_name)
        assert pty_ref == 'ERA5-Land'
        assert ref_vers == 'ERA5_LAND_V20190904'
        assert ref_vers_pty == 'v20190904'

        pty_ds1, ds1_vers, ds1_vers_pty = self.img.short_to_pretty(ds_short_names[0])
        assert pty_ds1 == 'C3S'
        assert ds1_vers == 'C3S_V201812'
        assert ds1_vers_pty == 'v201812'

        pty_ds2, ds2_vers, ds2_vers_pty = self.img.short_to_pretty(ds_short_names[1])
        assert pty_ds2 == 'SMOS IC'
        assert ds2_vers == 'SMOS_105_ASC'
        assert ds2_vers_pty == 'V.105 Ascending'

        # test fallback to globals - short name not from file
        pty_ref, ref_vers, ref_vers_pty = self.img.short_to_pretty('ASCAT', ignore_error=True)
        assert pty_ref == 'H-SAF ASCAT SSM CDR'
        assert ref_vers == 'unknown'
        assert pty_ref == 'unknown version'

    def test_get_var_meta(self):
        var = 'n_obs'
        nobs_meta = self.img.get_var_meta([var])
        assert nobs_meta[var]['metric'] == var
        assert nobs_meta[var]['ref_pretty_name'] == 'ERA5-Land'
        assert nobs_meta[var]['ref_version'] == 'ERA5_LAND_V20190904'
        assert nobs_meta[var]['ref_version_pretty_name'] == 'v20190904'
        {'n_obs': {'metric': 'n_obs', 'ref_no': 2, 'ref': 'ERA5_LAND', 'ds_no': [1, 3], 'ds': ['C3S', 'ERA5_LAND'],
                   'g': 0, 'ds_pretty_name': ['C3S', 'ERA5-Land'], 'ds_version': ['C3S_V201812', 'ERA5_LAND_V20190904'],
                   'ds_version_pretty_name': ['v201812', 'v20190904'], 'ref_pretty_name': 'ERA5-Land',
                   'ref_version': 'ERA5_LAND_V20190904', 'ref_version_pretty_name': 'v20190904'}}


if __name__ == '__main__':
    unittest.main()
