# -*- coding: utf-8 -*-

from qa4sm_reader import ncplot
import os

__author__ = "Lukas Racbhauer"
__copyright__ = "Lukas Racbhauer"
__license__ = "mit"

def get_path(case):
    if case=='ISMN':
        testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
        return os.path.join(os.path.dirname(__file__), 'test_data',testfile)
    elif case=='GLDAS':
        testfile = '4-GLDAS.SoilMoi0_10cm_inst_with_1-ESA_CCI_SM_combined.sm_with_2-SMAP.soil_moisture_with_3-SMOS.Soil_Moisture.nc'
        return os.path.join(os.path.dirname(__file__), 'test_data',testfile)
    elif case=='boxplot':
        return os.path.join(os.path.dirname(__file__), 'test_results','boxplot')
    elif case=='mapplot':
        return os.path.join(os.path.dirname(__file__), 'test_results','mapplot')
    elif case=='plot_all':
        return os.path.join(os.path.dirname(__file__), 'test_results','plot_all')
    else:
        return None

def test_get_var():
    filepath = get_path('ISMN')
    exp_result = ['R_between_5-ISMN_1-C3S',
                  'R_between_5-ISMN_2-SMAP',
                  'R_between_5-ISMN_3-ASCAT',
                  'R_between_5-ISMN_4-SMOS']
    return ncplot.get_var(filepath, 'R') == exp_result

def test_load_data():
    filepath = get_path('ISMN')
    variables = ['R_between_5-ISMN_1-C3S',
                  'R_between_5-ISMN_2-SMAP',
                  'R_between_5-ISMN_3-ASCAT',
                  'R_between_5-ISMN_4-SMOS']
    return ncplot.load_data(filepath, variables, extent=(-125,-109,30,40))

def test_get_varmeta():
    filepath = get_path('ISMN')
    variables = ['R_between_5-ISMN_1-C3S',
                  'R_between_5-ISMN_2-SMAP',
                  'R_between_5-ISMN_3-ASCAT',
                  'R_between_5-ISMN_4-SMOS']
    return ncplot.get_varmeta(filepath, variables)

def test_get_meta():
    filepath = get_path('ISMN')
    var = 'R_between_5-ISMN_1-C3S'
    return ncplot.get_meta(filepath, var)

def test_load():
    filepath=get_path('ISMN')
    metric = 'R'
    return ncplot.load(filepath, metric, extent=(-125,-109,30,40))

def test_boxplot():
    filepath = get_path('ISMN')
    out_dir = get_path('boxplot')
    ncplot.boxplot(filepath, 'R', out_dir=out_dir, out_type='png')

def test_boxplot2(): #demonstrate some more functionality
    filepath = get_path('GLDAS')
    out_dir = get_path('boxplot')
    variables = ncplot.get_var(filepath, 'R')[:-1]
    ncplot.boxplot(filepath, variables, out_dir=out_dir,
                   watermark_pos=None, out_type=['png', 'svg'], dpi=300,
                   printnumbers=False, add_title=False)

def test_scattermap():
    filepath = get_path('ISMN')
    out_dir = get_path('mapplot')
    var = ncplot.get_var(filepath,'R')[0] #take the first var
    ncplot.mapplot(filepath, var, out_dir=out_dir, out_type='png')

def test_gridmap():
    filepath = get_path('GLDAS')
    out_dir = get_path('mapplot')
    var = ncplot.get_var(filepath,'R')[0] #take the first var
    ncplot.mapplot(filepath, var, out_dir=out_dir, out_type='png')

def test_boxplot_extent():
    filepath = get_path('ISMN')
    out_dir = get_path('boxplot')
    out_name = 'test_boxplot_extent'
    out_type = ['png', 'svg']
    ncplot.boxplot(filepath, 'R', (-125,-109,30,40), out_dir, out_name, out_type)

def test_boxplot2_extent():
    filepath = get_path('GLDAS')
    out_dir = get_path('boxplot')
    out_name = 'test_boxplot2_extent'
    out_type = ['png', 'svg']
    ncplot.boxplot(filepath, 'R', (-11,0,51,56), out_dir, out_name, out_type)

def test_scattermap_extent():
    filepath = get_path('ISMN')
    out_dir = get_path('mapplot')
    out_name = 'test_scattermap_extent'
    out_type = ['png', 'svg']
    var = ncplot.get_var(filepath,'R')[0] #take the first var
    ncplot.mapplot(filepath, var, (-125,-109,30,40), out_dir, out_name, out_type,
                   map_resolution='10m', add_us_states=True)

def test_gridmap_extent():
    filepath = get_path('GLDAS')
    out_dir = get_path('mapplot')
    out_name = 'test_gridmap_extent'
    out_type = ['png', 'svg']
    var = ncplot.get_var(filepath,'R')[0] #take the first var
    ncplot.mapplot(filepath, var, (-11,0,51,56), out_dir, out_name, out_type,
                   map_resolution='10m')

def test_plot_all_extent():
    filepath = get_path('GLDAS')
    out_dir = get_path('plot_all')
    out_type = 'png'
    ncplot.plot_all(filepath, extent=(-11,0,51,56), out_dir=out_dir, out_type=out_type,
                   mapplot_kwargs={'map_resolution' : '10m'} )

if __name__ == '__main__':
    print(__file__)
    test_get_var()
    test_load_data()
    test_get_varmeta()
    test_get_meta()
    test_load()
    test_boxplot()
    test_boxplot2()
    test_scattermap()
    test_gridmap()
    test_boxplot_extent()
    test_boxplot2_extent()
    test_scattermap_extent()
    test_gridmap_extent()
    test_plot_all_extent()