from qa4smreader import ncplot
import os

def test_get_metric_var():
    testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    exp_result = ['R_between_5-ISMN_1-C3S',
                  'R_between_5-ISMN_2-SMAP',
                  'R_between_5-ISMN_3-ASCAT',
                  'R_between_5-ISMN_4-SMOS']
    return ncplot.get_metric_var(filepath, 'R') == exp_result

def test_load_data():
    testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    variables = ['R_between_5-ISMN_1-C3S',
                  'R_between_5-ISMN_2-SMAP',
                  'R_between_5-ISMN_3-ASCAT',
                  'R_between_5-ISMN_4-SMOS']
    return ncplot.load_data(filepath, variables, extent=(-125,-109,30,40))

def test_get_varmeta():
    testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    variables = ['R_between_5-ISMN_1-C3S',
                  'R_between_5-ISMN_2-SMAP',
                  'R_between_5-ISMN_3-ASCAT',
                  'R_between_5-ISMN_4-SMOS']
    return ncplot.get_varmeta(filepath, variables)

def test_get_globmeta():
    testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    variables = ['R_between_5-ISMN_1-C3S',
                  'R_between_5-ISMN_2-SMAP',
                  'R_between_5-ISMN_3-ASCAT',
                  'R_between_5-ISMN_4-SMOS']
    return ncplot.get_globmeta(filepath, variables)

def test_get_meta():
    testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    var = 'R_between_5-ISMN_1-C3S'
    return ncplot.get_meta(filepath, var)

def test_load():
    testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    metric = 'R'
    return ncplot.load(filepath, metric, extent=(-125,-109,30,40))

def test_boxplot():
    testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    out_dir = os.path.join('test_results', 'boxplot')
    ncplot.boxplot(filepath, 'R', out_dir=out_dir, out_type='png')

def test_boxplot2(): #demonstrate some more functionality
    testfile = '4-GLDAS.SoilMoi0_10cm_inst_with_1-ESA_CCI_SM_combined.sm_with_2-SMAP.soil_moisture_with_3-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    out_dir = os.path.join('test_results', 'boxplot')
    variables = ncplot.get_metric_var(filepath, 'R')[:-1]
    ncplot.boxplot(filepath, variables, out_dir=out_dir,
                   watermark_pos=None, out_type=['png', 'svg'], dpi=300,
                   printnumbers=False, add_title=False)

def test_scattermap():
    testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    out_dir = os.path.join('test_results', 'mapplot')
    var = ncplot.get_metric_var(filepath,'R')[0] #take the first var
    ncplot.mapplot(filepath, var, out_dir=out_dir, out_type='png')

def test_gridmap():
    testfile = '4-GLDAS.SoilMoi0_10cm_inst_with_1-ESA_CCI_SM_combined.sm_with_2-SMAP.soil_moisture_with_3-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    out_dir = os.path.join('test_results', 'mapplot')
    var = ncplot.get_metric_var(filepath,'R')[0] #take the first var
    ncplot.mapplot(filepath, var, out_dir=out_dir, out_type='png')

def test_boxplot_extent():
    testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    out_dir = os.path.join('test_results', 'boxplot')
    out_name = 'test_boxplot_extent'
    out_type = ['png', 'svg']
    ncplot.boxplot(filepath, 'R', (-125,-109,30,40), out_dir, out_name, out_type)

def test_boxplot2_extent():
    testfile = '4-GLDAS.SoilMoi0_10cm_inst_with_1-ESA_CCI_SM_combined.sm_with_2-SMAP.soil_moisture_with_3-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    out_dir = os.path.join('test_results', 'boxplot')
    out_name = 'test_boxplot2_extent'
    out_type = ['png', 'svg']
    ncplot.boxplot(filepath, 'R', (-11,0,51,56), out_dir, out_name, out_type)

def test_scattermap_extent():
    testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    out_dir = os.path.join('test_results', 'mapplot')
    out_name = 'test_scattermap_extent'
    out_type = ['png', 'svg']
    var = ncplot.get_metric_var(filepath,'R')[0] #take the first var
    ncplot.mapplot(filepath, var, (-125,-109,30,40), out_dir, out_name, out_type,
                   map_resolution='10m', add_us_states=True)

def test_gridmap_extent():
    testfile = '4-GLDAS.SoilMoi0_10cm_inst_with_1-ESA_CCI_SM_combined.sm_with_2-SMAP.soil_moisture_with_3-SMOS.Soil_Moisture.nc'
    filepath = os.path.join('test_data', testfile)
    out_dir = os.path.join('test_results', 'mapplot')
    out_name = 'test_gridmap_extent'
    out_type = ['png', 'svg']
    var = ncplot.get_metric_var(filepath,'R')[0] #take the first var
    ncplot.mapplot(filepath, var, (-11,0,51,56), out_dir, out_name, out_type,
                   map_resolution='10m')

if __name__ == '__main__':
    test_get_metric_var()
    test_load_data()
    test_get_varmeta()
    test_get_globmeta()
    test_get_meta()
    test_load()
    test_boxplot()
    test_boxplot2()
    test_scattermap()
    test_gridmap()
    test_boxplot_extent()
    test_boxplot2_extent()
    test_gridmap_extent()