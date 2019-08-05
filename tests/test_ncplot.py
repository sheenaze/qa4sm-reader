# -*- coding: utf-8 -*-


__author__ = "Lukas Racbhauer"
__copyright__ = "Lukas Racbhauer"
__license__ = "mit"


"""
Contains testing code for ncplot.py

Missing: 
* rare cases in get_value_range()
    * Gridded dataset with missing row/column, resulting in multiple stepsizes, 
      which are handled in '_get_grid' and '_float_gcd'
    * metric not given to dfplot
    * metric not in globals
    * force quantile
* init_plot()
    * plot without colorbar
    
"""


from qa4sm_reader import ncplot
import pandas as pd
import numpy as np
import os
import pytest
from pandas.util.testing import assert_frame_equal
import warnings
EXTENT_GRID = (-6.2, -5.3, 56, 58)  # GB, Scotland
EXTENT_SCATTER = (-125, -109, 30, 40)  # USA, California


old_cwd = os.getcwd()
os.chdir(os.path.join(os.path.dirname(__file__), 'test_results'))  # The default plot functions will store their stuff in CWD.


def get_path(case):
    if case == 'ISMN_nan':  # contains nan values.
        testfile = '6-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-ESA_CCI_SM_combined.sm_with_5-SMOS.Soil_Moisture.nc'
        return os.path.join(os.path.dirname(__file__), 'test_data', testfile)
    elif case == 'GLDAS_nan':  # contains nan values, has problems in panoply.
        testfile = '6-GLDAS.SoilMoi0_10cm_inst_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-ESA_CCI_SM_combined.sm_with_5-SMOS.Soil_Moisture.nc'
        return os.path.join(os.path.dirname(__file__), 'test_data', testfile)
    if case == 'ISMN':
        testfile = '3-ISMN.soil moisture_with_1-C3S.sm_with_2-ESA_CCI_SM_combined.sm.nc'
        # testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
        return os.path.join(os.path.dirname(__file__), 'test_data', testfile)
    elif case == 'GLDAS':
        testfile = '3-GLDAS.SoilMoi0_10cm_inst_with_1-C3S.sm_with_2-ESA_CCI_SM_combined.sm.nc'
        # testfile = '4-GLDAS.SoilMoi0_10cm_inst_with_1-ESA_CCI_SM_combined.sm_with_2-SMAP.soil_moisture_with_3-SMOS.Soil_Moisture.nc'
        return os.path.join(os.path.dirname(__file__), 'test_data', testfile)
    elif case == 'boxplot':
        return os.path.join(os.path.dirname(__file__), 'test_results', 'boxplot')
    elif case == 'mapplot':
        return os.path.join(os.path.dirname(__file__), 'test_results', 'mapplot')
    elif case == 'plot_all':
        return os.path.join(os.path.dirname(__file__), 'test_results', 'plot_all')
    else:
        return None


def test__get_dir_name_type():
    assert ncplot._get_dir_name_type(None, 'MyName', None) == (os.getcwd(), 'MyName', {'.png'})
    assert ncplot._get_dir_name_type('H:\\MyFolder', 'MyName.png', ['pdf', '.svg']) == \
           ('H:\\MyFolder', 'MyName', {'.png', '.svg', '.pdf'})


def test_get_var():
    filepath = get_path('ISMN_nan')
    exp_result = ['R_between_6-ISMN_1-C3S',
                  'R_between_6-ISMN_2-SMAP',
                  'R_between_6-ISMN_3-ASCAT',
                  'R_between_6-ISMN_4-ESA_CCI_SM_combined',
                  'R_between_6-ISMN_5-SMOS']
    assert ncplot.get_var(filepath, 'R') == exp_result


def test_load_data():
    filepath = get_path('ISMN_nan')
    variables = ['R_between_6-ISMN_2-SMAP',
                 'R_between_6-ISMN_3-ASCAT']
    exp_data = np.array([[35.93326, -120.90684, 0.7949211, 0.7959337],
                         [32.88921, -117.10469, 0.5757222, 0.63345855]], dtype=np.float32)
    exp_index = [0, 1]
    exp_columns = ['lat', 'lon', 'R_between_6-ISMN_2-SMAP', 'R_between_6-ISMN_3-ASCAT']
    exp_result = pd.DataFrame(exp_data, exp_index, exp_columns)
    df = ncplot.load_data(filepath, variables, extent=(-130, -110, 30, 36))  # TODO: change to fixture, update exp_data (-130, -110, 30, 36) -> (-125, -109, 30, 40)
    assert_frame_equal(df, exp_result)


def test_get_varmeta():
    filepath = get_path('ISMN')
    variables = ['R_between_3-ISMN_1-C3S', 'R_between_3-ISMN_2-ESA_CCI_SM_combined']
    exp_result = {'R_between_3-ISMN_1-C3S':
                      {'metric': 'R',
                       'ref_no': 3, 'ref': 'ISMN',
                       'ds_no': 1, 'ds': 'C3S', 'ds_pretty_name': 'C3S',
                       'ds_version': 'C3S_V201812', 'ds_version_pretty_name': 'v201812',
                       'ref_pretty_name': 'ISMN', 'ref_version': 'ISMN_V20180712_TEST',
                       'ref_version_pretty_name': '20180712 testset'},
                  'R_between_3-ISMN_2-ESA_CCI_SM_combined':
                      {'metric': 'R',
                       'ref_no': 3, 'ref': 'ISMN',
                       'ds_no': 2, 'ds': 'ESA_CCI_SM_combined',
                       'ds_pretty_name': 'ESA CCI SM combined',
                       'ds_version': 'ESA_CCI_SM_C_V04_4', 'ds_version_pretty_name': 'v04.4',
                       'ref_pretty_name': 'ISMN', 'ref_version': 'ISMN_V20180712_TEST',
                       'ref_version_pretty_name': '20180712 testset'}}
    assert ncplot.get_varmeta(filepath, variables) == exp_result


def test_get_meta():
    filepath = get_path('ISMN')
    var = 'R_between_3-ISMN_1-C3S'
    exp_result = {'metric': 'R', 'ref_no': 3, 'ref': 'ISMN', 'ds_no': 1, 'ds': 'C3S', 'ds_pretty_name': 'C3S',
                  'ds_version': 'C3S_V201812', 'ds_version_pretty_name': 'v201812', 'ref_pretty_name': 'ISMN',
                  'ref_version': 'ISMN_V20180712_TEST', 'ref_version_pretty_name': '20180712 testset'}
    assert ncplot.get_meta(filepath, var) == exp_result


def test_load():
    filepath = get_path('ISMN')
    metric = 'R'
    exp_data = np.array([[35.93326, -120.90684, 0.81058246, 0.8078558],
                         [32.88921, -117.10469, 0.562755, 0.5847081],
                         [33.8, -115.31, 0.18982203, 0.1902729],
                         [39.983, -114., 0.5147627, 0.49328756],
                         [39.45, -115.98, 0.32813886, 0.34835243],
                         [38.38719, -120.90653, 0.7411028, 0.7471703],
                         [38.3877, -120.90604, 0.91249835, 0.91023356],
                         [38.43081, -120.96736, 0.8609224, 0.86377543],
                         [38.3208, -123.0747, 0.7248938, 0.7531663],
                         [37.2381, -120.8825, 0.8336041, 0.83316183]],
                        dtype=np.float32)
    exp_index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    exp_columns = ['lat', 'lon', 'R_between_3-ISMN_1-C3S', 'R_between_3-ISMN_2-ESA_CCI_SM_combined']
    exp_df = pd.DataFrame(exp_data, exp_index, exp_columns)
    exp_varmeta = {'R_between_3-ISMN_1-C3S':
                      {'metric': 'R',
                       'ref_no': 3, 'ref': 'ISMN',
                       'ds_no': 1, 'ds': 'C3S', 'ds_pretty_name': 'C3S',
                       'ds_version': 'C3S_V201812', 'ds_version_pretty_name': 'v201812',
                       'ref_pretty_name': 'ISMN', 'ref_version': 'ISMN_V20180712_TEST',
                       'ref_version_pretty_name': '20180712 testset'},
                  'R_between_3-ISMN_2-ESA_CCI_SM_combined':
                      {'metric': 'R',
                       'ref_no': 3, 'ref': 'ISMN',
                       'ds_no': 2, 'ds': 'ESA_CCI_SM_combined',
                       'ds_pretty_name': 'ESA CCI SM combined',
                       'ds_version': 'ESA_CCI_SM_C_V04_4', 'ds_version_pretty_name': 'v04.4',
                       'ref_pretty_name': 'ISMN', 'ref_version': 'ISMN_V20180712_TEST',
                       'ref_version_pretty_name': '20180712 testset'}}
    df, varmeta = ncplot.load(filepath, metric, extent=EXTENT_SCATTER)
    assert varmeta == exp_varmeta
    assert_frame_equal(df, exp_df)


# === Boxplot ===
def test_boxplot_ISMN_default():
    filepath = get_path('ISMN')
    ncplot.boxplot(filepath, 'R')
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(os.getcwd()))  # TODO: print full filename


def test_boxplot_ISMN_nan_default():
    filepath = get_path('ISMN_nan')
    ncplot.boxplot(filepath, 'rho')
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(os.getcwd()))  # TODO: print full filename


def test_boxplot_GLDAS_default():
    filepath = get_path('GLDAS')
    ncplot.boxplot(filepath, 'R')
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(os.getcwd()))


def test_boxplot_GLDAS_nan_default():
    filepath = get_path('GLDAS_nan')
    ncplot.boxplot(filepath, 'rho')
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(os.getcwd()))


def test_boxplot_GLDAS_options():
    out_dir = get_path('boxplot')
    filepath = get_path('GLDAS')
    out_name = 'test_boxplot_GLDAS_options'
    variables = ncplot.get_var(filepath, 'R')[:-1]
    ncplot.boxplot(filepath, variables, out_dir=out_dir, out_name=out_name,
                   out_type=['png', '.svg'], dpi=300,
                   print_stat=False, add_title=False, watermark_pos='bottom')
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(out_dir))


def test_boxplot_ISMN_extent():
    filepath = get_path('ISMN')
    out_dir = get_path('boxplot')
    out_name = 'test_boxplot_ISMN_extent'
    out_type = 'png'
    ncplot.boxplot(filepath, 'R', (-125, -109, 30, 40), out_dir, out_name, out_type)
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(out_dir))


def test_boxplot_GLDAS_nan_extent():
    filepath = get_path('GLDAS_nan')
    out_dir = get_path('boxplot')
    out_name = 'test_boxplot_GLDAS_nan_extent'
    ncplot.boxplot(filepath, 'R', EXTENT_GRID, out_dir, out_name)
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(out_dir))


# === mapplot ===
def test_mapplot_ISMN_default(): # TODO: takes long. why?
    filepath = get_path('ISMN')
    var = ncplot.get_var(filepath, 'R')[0]  # take the first var
    ncplot.mapplot(filepath, var)
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(os.getcwd()))


def test_mapplot_ISMN_nan_default(): # TODO: takes extremely long (minutes). why?
    filepath = get_path('ISMN_nan')
    var = ncplot.get_var(filepath, 'rho')[0]  # take the first var
    ncplot.mapplot(filepath, var)
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(os.getcwd()))


def test_mapplot_GLDAS_default():  # 16
    filepath = get_path('GLDAS')
    var = ncplot.get_var(filepath, 'R')[0]  # take the first var
    ncplot.mapplot(filepath, var)
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(os.getcwd()))


def test_mapplot_GLDAS_nan_default():  # 17
    filepath = get_path('GLDAS_nan')
    var = ncplot.get_var(filepath, 'rho')[0]  # take the first var
    ncplot.mapplot(filepath, var)
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(os.getcwd()))


def test_mapplot_ISMN_extent():  # 18
    filepath = get_path('ISMN')
    out_dir = get_path('mapplot')
    out_name = 'mapplot_ISMN_extent'
    out_type = ['png', 'pdf', 'svg']
    var = ncplot.get_var(filepath, 'R')[0]  # take the first var
    ncplot.mapplot(filepath, var, EXTENT_SCATTER, out_dir, out_name, out_type,
                   map_resolution='10m', add_us_states=True)
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(out_dir))


def test_mapplot_GLDAS_extent():  # 19
    filepath = get_path('GLDAS')
    out_dir = get_path('mapplot')
    out_name = 'mapplot_GLDAS_extent'
    out_type = 'png'
    var = ncplot.get_var(filepath, 'R')[0]  # take the first var
    ncplot.mapplot(filepath, var, EXTENT_GRID, out_dir, out_name, out_type,
                   map_resolution='10m')
    warnings.warn('Test does not assert output images. Have a look at {}.'.format(out_dir))


def test_plot_all_extent():
    filepath = get_path('GLDAS')
    out_dir = get_path('plot_all')
    out_type = 'png'
    ncplot.plot_all(filepath, extent=EXTENT_GRID, out_dir=out_dir, out_type=out_type,
                    boxplot_kwargs={'watermark_pos' : None}, mapplot_kwargs={'figsize' : [11.32, 6.10]})
