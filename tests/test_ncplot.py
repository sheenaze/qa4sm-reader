# -*- coding: utf-8 -*-

from qa4sm_reader import ncplot
import pandas as pd
import numpy as np
import os
import pytest
from pandas.util.testing import assert_frame_equal

__author__ = "Lukas Racbhauer"
__copyright__ = "Lukas Racbhauer"
__license__ = "mit"


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
    df = ncplot.load_data(filepath, variables, extent=(-130, -110, 30, 36))
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
    df, varmeta = ncplot.load(filepath, metric, extent=(-125, -109, 30, 40))
    assert varmeta == exp_varmeta
    assert_frame_equal(df, exp_df)


# def test_boxplot():
#     filepath = get_path('ISMN')
#     out_dir = get_path('boxplot')
#     ncplot.boxplot(filepath, 'R', out_dir=out_dir, out_type='png')
#
#
# def test_boxplot2():  # demonstrate some more functionality
#     filepath = get_path('GLDAS')
#     out_dir = get_path('boxplot')
#     variables = ncplot.get_var(filepath, 'R')[:-1]
#     ncplot.boxplot(filepath, variables, out_dir=out_dir,
#                    watermark_pos=None, out_type=['png', 'svg'], dpi=300,
#                    printnumbers=False, add_title=False)
#
#
# def test_scattermap():
#     filepath = get_path('ISMN')
#     out_dir = get_path('mapplot')
#     var = ncplot.get_var(filepath, 'R')[0]  # take the first var
#     ncplot.mapplot(filepath, var, out_dir=out_dir, out_type='png')
#
#
# def test_gridmap():
#     filepath = get_path('GLDAS')
#     out_dir = get_path('mapplot')
#     var = ncplot.get_var(filepath, 'R')[0]  # take the first var
#     ncplot.mapplot(filepath, var, out_dir=out_dir, out_type='png')
#
#
# def test_boxplot_extent():
#     filepath = get_path('ISMN')
#     out_dir = get_path('boxplot')
#     out_name = 'test_boxplot_extent'
#     out_type = ['png', 'svg']
#     ncplot.boxplot(filepath, 'R', (-125, -109, 30, 40), out_dir, out_name, out_type)
#
#
# def test_boxplot2_extent():
#     filepath = get_path('GLDAS')
#     out_dir = get_path('boxplot')
#     out_name = 'test_boxplot2_extent'
#     out_type = ['png', 'svg']
#     ncplot.boxplot(filepath, 'R', (-11, 0, 51, 56), out_dir, out_name, out_type)
#
#
# def test_scattermap_extent():
#     filepath = get_path('ISMN')
#     out_dir = get_path('mapplot')
#     out_name = 'test_scattermap_extent'
#     out_type = ['png', 'svg']
#     var = ncplot.get_var(filepath, 'R')[0]  # take the first var
#     ncplot.mapplot(filepath, var, (-125, -109, 30, 40), out_dir, out_name, out_type,
#                    map_resolution='10m', add_us_states=True)
#
#
# def test_gridmap_extent():
#     filepath = get_path('GLDAS')
#     out_dir = get_path('mapplot')
#     out_name = 'test_gridmap_extent'
#     out_type = ['png', 'svg']
#     var = ncplot.get_var(filepath, 'R')[0]  # take the first var
#     ncplot.mapplot(filepath, var, (-11, 0, 51, 56), out_dir, out_name, out_type,
#                    map_resolution='10m')
#
#
# def test_plot_all_extent():
#     filepath = get_path('GLDAS')
#     out_dir = get_path('plot_all')
#     out_type = 'png'
#     ncplot.plot_all(filepath, extent=(-11, 0, 51, 56), out_dir=out_dir, out_type=out_type,
#                     mapplot_kwargs={'map_resolution': '10m'})
