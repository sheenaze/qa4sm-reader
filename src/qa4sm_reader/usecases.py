# -*- coding: utf-8 -*-


__author__ = "Lukas Racbhauer, Wolfgang Preimesberger"
__copyright__ = "2019, TU Wien, Department of Geodesy and Geoinformation"
__license__ = "mit"


'''
Usecase demonstrating the functionality of qa4sm_reader.

The first section deals with ncplot, which contains functions for handling qa4sm output files including metadata.
The second section deals with dfplot, which contains lower level functions for plotting.
'''
# === Using qa4sm_reader to generate plots for qa4sm service ===
if True:
    import logging

    import re
    from os import path, remove
    from zipfile import ZipFile

    import matplotlib.pyplot as plt
    from qa4sm_reader import ncplot, dfplot

    __logger = logging.getLogger(__name__)

    def generate_all_graphs(validataion_run, outfolder):
        if not validation_run.output_file:
            return None

        zipfilename = path.join(outfolder, 'graphs.zip')
        __logger.debug('Trying to create zipfile {}'.format(zipfilename))

        filepath = validation_run.output_file.path  # get filepath from validation run object

        with ZipFile(zipfilename, 'w', ZIP_DEFLATED) as myzip:
            for metric in ncplot.get_metrics(filepath):  # loop over available metrics
                # === load data and metadata ===
                df, varmeta = ncplot.load(filepath, metric)

                # === boxplot ===
                fig, ax = dfplot.boxplot(df, varmeta)

                # === save ===
                png_filename = path.join(outfolder, 'boxplot_{}.png'.format(metric))
                svg_filename = path.join(outfolder, 'boxplot_{}.svg'.format(metric))
                plt.savefig(png_filename, dpi='figure')
                plt.savefig(svg_filename)
                plt.close()

                # === write to zip ===
                arcname = path.basename(png_filename)
                myzip.write(png_filename, arcname=arcname)
                arcname = path.basename(svg_filename)
                myzip.write(svg_filename, arcname=arcname)
                remove(svg_filename)  # we don't need the vector image anywhere but in the zip

                for var in ncplot.get_variables(filepath, metric):
                    # === plot ===
                    fig, ax = dfplot.mapplot(df, var=var, meta=varmeta[var])

                    # === save ===
                    ds_match = re.match(r'.*_between_(([0-9]+)-(.*)_([0-9]+)-(.*))', var)
                    if ds_match:
                        pair_name = ds_match.group(1)
                    else:
                        pair_name = var  # e.g. n_obs

                    if metric == pair_name:  # e.g. n_obs
                        filename = 'overview_{}'.format(metric)
                    else:
                        filename = 'overview_{}_{}'.format(pair_name, metric)

                    png_filename = path.join(outfolder, filename + '.png')
                    svg_filename = path.join(outfolder, filename + '.svg')

                    plt.savefig(png_filename, dpi='figure')
                    plt.savefig(svg_filename)
                    plt.close()

                    # === write to zip ===
                    arcname = path.basename(png_filename)
                    myzip.write(png_filename, arcname=arcname)
                    arcname = path.basename(svg_filename)
                    myzip.write(svg_filename, arcname=arcname)
                    remove(svg_filename)  # we don't need the vector image anywhere but in the zip



from qa4sm_reader.ncplot import mapplot, get_variables, boxplot
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
        variable = get_variables(filepath, 'rho')[0] #['R_between_5-ISMN_1-C3S']#, 'R_between_5-ISMN_2-SMAP', 'R_between_5-ISMN_3-ASCAT', 'R_between_5-ISMN_4-SMOS']
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