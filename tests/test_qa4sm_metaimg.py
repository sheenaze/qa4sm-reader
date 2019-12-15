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
        self.img = QA4SM_MetaImg(self.testfile_path, extent=(144., 149., -43, -40))

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
        assert ref_vers_pty == 'unknown __version'

    def test_compile_var(self):
        # common var
        var = 'n_obs'
        g = self.img._metr_grp(var)
        assert g == 0
        meta, n_sats = self.img._compile_var(var, var_group=g)
        assert meta['metric'] == var
        assert meta['ref'] == 'ERA5_LAND'
        assert meta['ref_no'] is None
        assert meta['ds1'] == 'C3S'
        assert meta['ds1_no'] is None
        assert meta['ds2'] == 'SMOS'
        assert meta['ds2_no'] is None
        assert n_sats == self.n_ds - 1 # because this excludes the reference

        # wrong var
        var = 'thisdoesnotexist'
        g = self.img._metr_grp(var)
        assert g is None

        # double var
        var = 'R_between_3-ERA5_LAND_and_1-C3S'
        meta, n_sats = self.img._compile_var(var, var_group=2)
        assert meta['metric'] == 'R'
        assert meta['ref'] == 'ERA5_LAND'
        assert meta['ref_no'] == 3
        assert meta['ds1'] == 'C3S'
        assert meta['ds1_no'] == 1
        assert n_sats == 1 # because its only c3s

    def test_get_var_meta(self):
        all_var_meta = self.img.get_var_meta()
        assert all_var_meta['R_between_3-ERA5_LAND_and_1-C3S']['metric'] == 'R'
        assert all_var_meta['R_between_3-ERA5_LAND_and_1-C3S']['ref'] == 'ERA5_LAND'
        assert all_var_meta['R_between_3-ERA5_LAND_and_1-C3S']['ds1'] == 'C3S'

    def test_load_metric_and_meta(self):
        df, meta = self.img.load_metric_and_meta('n_obs')
        assert len(df.index.values) == 217
        assert list(meta.keys()) == ['n_obs']
        df, meta = self.img.load_metric_and_meta('RMSD')
        assert len(df.index.values) == 211
        assert list(meta.keys()) == ['RMSD_between_3-ERA5_LAND_and_1-C3S',
                                     'RMSD_between_3-ERA5_LAND_and_2-SMOS']
        assert meta['RMSD_between_3-ERA5_LAND_and_1-C3S']['ref'] == 'ERA5_LAND'
        assert meta['RMSD_between_3-ERA5_LAND_and_1-C3S']['ds1'] == 'C3S'
        assert meta['RMSD_between_3-ERA5_LAND_and_1-C3S']['var_group'] == 2
        assert meta['RMSD_between_3-ERA5_LAND_and_1-C3S']['ref_pretty_name'] == 'ERA5-Land'

        assert meta['RMSD_between_3-ERA5_LAND_and_2-SMOS']['ds1_version'] == 'SMOS_105_ASC'
        assert meta['RMSD_between_3-ERA5_LAND_and_2-SMOS']['ds1_version_pretty_name'] == 'V.105 Ascending'


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestQA4SMMetaImgBasicIntercomp("test_get_var_meta"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
