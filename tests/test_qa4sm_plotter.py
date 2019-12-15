# -*- coding: utf-8 -*-

from src.qa4sm_reader.plotter import QA4SM_MetaImg_Plotter
import os
import unittest
import tempfile

class TestQA4SMMetaImgBasicPlotter(unittest.TestCase):

    def setUp(self) -> None:
        self.testfile = '3-ERA5_LAND.swvl1_with_1-C3S.sm_with_2-SMOS.Soil_Moisture.nc'
        self.testfile_path = os.path.join(os.path.dirname(__file__), '..','tests',
                                          'test_data', self.testfile)
        self.img = QA4SM_MetaImg_Plotter(self.testfile_path,
                                         extent=(132., 156., -44, -40))

        self.n_ds = len(self.testfile.split('_with_'))

    def test_get_dirname_type(self):
        dirpath = tempfile.mkdtemp()
        out_dir, out_name, out_type = self.img._get_dir_name_type(
            'test.png', out_type='png', out_dir=dirpath)
        assert out_dir == dirpath
        assert out_name == 'test'
        assert out_type == {'.png'}

    def test_ds_pretty_names(self):
        varmeta = self.img.get_var_meta(['n_obs'])
        (ref_pretty, ref_version_pretty), (ds_pretty, ds_version_pretty) = \
        self.img._ds_pretty_names(varmeta['n_obs'])
        assert ref_pretty == 'ERA5-Land'
        assert ref_version_pretty == 'v20190904'
        assert ds_pretty == ['C3S', 'SMOS IC'] # ALL 3 datasets are in the common var
        assert ds_version_pretty == ['v201812', 'V.105 Ascending']

        varmeta = self.img.get_var_meta(['R_between_3-ERA5_LAND_and_1-C3S'])
        (ref_pretty, ref_version_pretty), (ds_pretty, ds_version_pretty) = \
        self.img._ds_pretty_names(varmeta['R_between_3-ERA5_LAND_and_1-C3S'])
        assert ref_pretty == 'ERA5-Land'
        assert ref_version_pretty == 'v20190904'
        assert ds_pretty == ['C3S'] # Only the ref and one sat values
        assert ds_version_pretty == ['v201812']

    def test_boxplot(self):
        metrics = self.img.metrics_in_file(False)
        for metric in metrics:
            #dirpath = tempfile.mkdtemp()
            dirpath = r'C:\Temp\qa4smreader_plots\test\boxes'
            self.img.boxplot_basic(metric, out_dir=dirpath, out_name=None, out_type='png')
            self.img.boxplot_basic(metric, out_dir=dirpath, out_name=None, out_type='svg')

    def test_mapplot(self):
        vars = self.img.vars_in_file(True)
        for var in vars:
            #dirpath = tempfile.mkdtemp()
            dirpath = r'C:\Temp\qa4smreader_plots\test\maps'
            self.img.mapplot(var, out_dir=dirpath, out_name=None, out_type='png')
            self.img.mapplot(var, out_dir=dirpath, out_name=None, out_type='svg')

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestQA4SMMetaImgBasicPlotter("test_boxplot"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
