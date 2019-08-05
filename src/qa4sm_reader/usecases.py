# -*- coding: utf-8 -*-


__author__ = "Lukas Racbhauer, Wolfgang Preimesberger"
__copyright__ = "2019, TU Wien, Department of Geodesy and Geoinformation"
__license__ = "mit"


'''
Module description
'''
# TODO # (+) 

# NOTES #

from qa4sm_reader.ncplot import mapplot, get_var, boxplot
import os
import cartopy.crs as ccrs

this_dir = os.path.dirname(__file__)
test_dir = os.path.join(this_dir, '../..', 'tests')
out_path = os.path.join(test_dir, 'test_data', 'out')

if not os.path.isdir(out_path):
    os.mkdir(out_path)

testfiles = {'GLDAS-3' :
                 '3-GLDAS.SoilMoi0_10cm_inst_with_1-C3S.sm_with_2-ESA_CCI_SM_combined.sm.nc',
             'GLDAS-6':
                '6-GLDAS.SoilMoi0_10cm_inst_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-ESA_CCI_SM_combined.sm_with_5-SMOS.Soil_Moisture.nc',
             'ISMN-3' :
                 '3-ISMN.soil moisture_with_1-C3S.sm_with_2-ESA_CCI_SM_combined.sm.nc',
             'ISMN-6' :
                '6-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-ESA_CCI_SM_combined.sm_with_5-SMOS.Soil_Moisture.nc'
             }

def start_usecase(usecase, store_output=False):
    if usecase == 'box_ismn':
        metrics = ['ubRMSD', 'rmsd']
        filepath = os.path.join(test_dir, 'test_data', testfiles['ISMN-6'])
        for m in metrics:
            box = boxplot(filepath, m, out_dir=out_path, watermark_pos='top', dpi=100,
                          out_name='ISMN-6_box_{}.png'.format(m) if store_output else None)

    if usecase == 'box_gldas':
        # boxplots cci, smap, smos wrt. gldas
        filepath = os.path.join(test_dir, 'test_data', testfiles['GLDAS-6'])

        metrics = ['R', 'rho', 'ubRMSD']

        for m in metrics:
            box = boxplot(filepath, m, out_dir=out_path, #todo: there was a 'format' keyword that did not work
                    out_name='GLDAS-6_box_{}.png'.format(m) if store_output else None)

    if usecase == 'map_ismn':
        # map with ismn results, not stored
        variables = ['R_between_6-ISMN_1-C3S', 'R_between_6-ISMN_2-SMAP']# 'R_between_5-ISMN_3-ASCAT', 'R_between_5-ISMN_4-SMOS']
        filepath = os.path.join(test_dir, 'test_data', testfiles['ISMN-6'])
        for var in variables:
            themap = mapplot(filepath, var, out_dir=out_path,
                             watermark_pos='bottom', #todo: there was a 'format' keyword that did not work
                             projection=ccrs.PlateCarree(), dpi=300,
                             out_name='map_ismn_{}.png'.format(var) if store_output else None)

    if usecase == 'map_gldas':
        # map with gldas results, not stored
        filepath = os.path.join(test_dir, 'test_data', testfiles['GLDAS-3'])
        variable = get_var(filepath, 'rho')[0] #['R_between_5-ISMN_1-C3S']#, 'R_between_5-ISMN_2-SMAP', 'R_between_5-ISMN_3-ASCAT', 'R_between_5-ISMN_4-SMOS']
        themap = mapplot(filepath, variable, out_dir=out_path,
                         watermark_pos='bottom',  #todo: there was a 'format' keyword that did not work
                         projection=ccrs.PlateCarree(), dpi=300,
                         out_name='map_gldas_rho.png' if store_output else None)

def usecase():
    #start_usecase(usecase='qa4sm_ismn')
    #start_usecase(usecase='qa4sm_ismn_save')
    #start_usecase(usecase='qa4sm_gldas')
    #start_usecase(usecase='qa4sm_gldas_save')
    #start_usecase(usecase='qa4sm_ismn-error') #specifies inconsistent variables
    #return start_usecase(usecase='asdf')
    #return start_usecase(usecase='map')
    #return start_usecase(usecase='boxplot-metric')

    pass


if __name__ == '__main__':
    start_usecase(usecase='box_ismn', store_output=True)
    start_usecase(usecase='box_gldas', store_output=True)
    start_usecase(usecase='map_ismn', store_output=True)
    start_usecase(usecase='map_gldas', store_output=True)