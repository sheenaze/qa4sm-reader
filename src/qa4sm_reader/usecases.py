# -*- coding: utf-8 -*-

'''
Module description
'''
# TODO # (+) 

# NOTES #

from qa4sm_reader import ncplot
import os
import cartopy.crs as ccrs

this_dir = os.path.dirname(__file__)
out_path = os.path.join(this_dir, 'test_data', 'out')
testfiles = {'4-GLDAS' : '4-GLDAS.SoilMoi0_10cm_inst_with_1-ESA_CCI_SM_combined.sm_with_2-SMAP.soil_moisture_with_3-SMOS.Soil_Moisture.nc',
             '4-ISMN' : '4-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ESA_CCI_SM_combined.sm.nc',
             '5-ISMN' : '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'}


__author__ = "Lukas Racbhauer"
__copyright__ = "Lukas Racbhauer"
__license__ = "mit"


def start_usecase(usecase):
    if usecase == 'qa4sm_ismn':
        variables = ['ubRMSD_between_4-ISMN_1-C3S',
                     'ubRMSD_between_4-ISMN_2-SMAP',
                     'ubRMSD_between_4-ISMN_3-ESA_CCI_SM_combined']
        filepath = os.path.join(this_dir, 'test_data', testfiles['4-ISMN'])
        ncplot.boxplot(filepath, variables, watermark_pos='top')


    if usecase == 'qa4sm_ismn_save':
        variables = ['ubRMSD_between_4-ISMN_1-C3S',
                     'ubRMSD_between_4-ISMN_2-SMAP',
                     'ubRMSD_between_4-ISMN_3-ESA_CCI_SM_combined']
        filepath = os.path.join(this_dir, 'test_data', testfiles['4-ISMN'])
        ncplot.boxplot(filepath,variables,out_dir=out_path,
                          format=['png','svg'],dpi=100)

    if usecase == 'qa4sm_gldas':
        variables = ['p_R_between_4-GLDAS_1-ESA_CCI_SM_combined',
                     'p_R_between_4-GLDAS_2-SMAP',
                     'p_R_between_4-GLDAS_3-SMOS']
        filepath = os.path.join(this_dir, 'test_data', testfiles['4-GLDAS'])
        ncplot.boxplot(filepath,variables)

    if usecase == 'qa4sm_gldas_save':
        variables = ['p_R_between_4-GLDAS_1-ESA_CCI_SM_combined',
                     'p_R_between_4-GLDAS_2-SMAP',
                     'p_R_between_4-GLDAS_3-SMOS']
        filepath = os.path.join(this_dir, 'test_data', testfiles['4-GLDAS'])
        ncplot.boxplot(filepath,variables,out_dir=out_path,
                          format=['png','svg'])

    if usecase == 'map':
        variable = ['R_between_5-ISMN_1-C3S']#, 'R_between_5-ISMN_2-SMAP', 'R_between_5-ISMN_3-ASCAT', 'R_between_5-ISMN_4-SMOS']
        filepath = os.path.join(this_dir, 'test_data', testfiles['5-ISMN'])
        return ncplot.mapplot(filepath,variable,out_dir=out_path,
                                 watermark_pos='bottom', format='png',
                                 projection=ccrs.PlateCarree(), dpi=300)#,
                                 # llc=(-175,-48.54),
                                 # urc=(175,78.55))
    if usecase == 'map_gldas':
        filepath = os.path.join(this_dir, 'test_data', testfiles['4-GLDAS'])
        variable = ncplot.get_metric_var(filepath, 'rho')[0] #['R_between_5-ISMN_1-C3S']#, 'R_between_5-ISMN_2-SMAP', 'R_between_5-ISMN_3-ASCAT', 'R_between_5-ISMN_4-SMOS']
        return ncplot.mapplot(filepath,variable,out_dir=out_path,
                                 watermark_pos='bottom', format='png',
                                 projection=ccrs.PlateCarree(), dpi=300) #,
                                  #llc=(-120,20), urc=(-95,40))

def usecase():
    #start_usecase(usecase='qa4sm_ismn')
    #start_usecase(usecase='qa4sm_ismn_save')
    #start_usecase(usecase='qa4sm_gldas')
    #start_usecase(usecase='qa4sm_gldas_save')
    #start_usecase(usecase='qa4sm_ismn-error') #specifies inconsistent variables
    #return start_usecase(usecase='asdf')
    #return start_usecase(usecase='map')
    return start_usecase(usecase='map_gldas')
    #return start_usecase(usecase='boxplot-metric')

if __name__ == '__main__':
    usecases.usecase()