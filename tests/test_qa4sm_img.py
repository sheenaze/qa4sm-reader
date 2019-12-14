# -*- coding: utf-8 -*-

from src.qa4sm_reader.img import QA4SMImg
import os
import re
import numpy as np
import unittest
from src.qa4sm_reader import globals

class TestQA4SMImgBasicIntercomp(unittest.TestCase):

    def setUp(self) -> None:
        self.testfile = '3-ERA5_LAND.swvl1_with_1-C3S.sm_with_2-SMOS.Soil_Moisture.nc'
        self.testfile_path = os.path.join(os.path.dirname(__file__), '..','tests',
                                          'test_data', self.testfile)
        self.img = QA4SMImg(self.testfile_path)

        self.n_ds = len(self.testfile.split('_with_'))

    def test_parse_filename(self):
        print('test_parse_filename')
        ds_and_vars = self.img.parse_filename()
        parts = self.testfile.split('_with_')
        parts[-1] = parts[-1][:-3] # drop the .nc from the last part
        assert [ds_and_vars['i_ref'], ds_and_vars['ref'], ds_and_vars['ref_var']] == \
               re.split(r"-|\.", parts[0])
        assert [ds_and_vars['i_ds1'], ds_and_vars['ds1'], ds_and_vars['var1']] == \
               re.split(r"-|\.", parts[1])
        assert [ds_and_vars['i_ds2'], ds_and_vars['ds2'], ds_and_vars['var2']] == \
               re.split(r"-|\.", parts[2])

    def test_metrics_in_file(self):
        print('test_metrics_in_file')
        # with grouped return value
        m_groups = self.img.metrics_in_file(group=True)
        assert m_groups['common'] == globals.metric_groups[0]
        for m in m_groups['double']:  # tau is not in the results
            assert m in globals.metric_groups[2]
        assert m_groups['triple'] == []  #  this is not the TC test case

        # with merged return value
        ms = self.img.metrics_in_file(group=False)
        for m in ms:
            assert any([m in l for l in list(globals.metric_groups.values())])

    def test_vars_in_file(self):
        print('test_vars_in_file')
        vars = self.img.vars_in_file(exclude_empty=False)
        vars_should = ['n_obs']
        for metric in globals.metric_groups[2]:
            vars_should.append('{}_between_3-ERA5_LAND_and_1-C3S'.format(metric))
            vars_should.append('{}_between_3-ERA5_LAND_and_2-SMOS'.format(metric))
        vars_should = np.sort(np.array(vars_should))
        assert all(vars == vars_should)

        vars = self.img.vars_in_file(exclude_empty=True)
        assert len(vars) <= len(vars_should)

    def test_load_metrics(self):
        print('test_load_metrics')
        metrics_in_file = self.img.metrics_in_file(group=False)
        for metric in metrics_in_file:
            print(metric)
            df, vars = self.img.load_metric(metric)

            if metric in globals.metric_groups[0]:
                assert len(df.columns) == 1
            else:
                assert len(df.columns) == (self.n_ds - 1)

if __name__ == '__main__':
    unittest.main()
