# -*- coding: utf-8 -*-
import qa4sm_reader.plot
import qa4sm_reader.read

__author__ = "Lukas Racbhauer, Wolfgang Preimesberger"
__copyright__ = "2019, TU Wien, Department of Geodesy and Geoinformation"
__license__ = "mit"


'''
Usecase demonstrating the functionality of qa4sm_reader.

The first section deals with ncplot, which contains functions for handling qa4sm output files including metadata.
The second section deals with dfplot, which contains lower level functions for plotting.
'''


import os
import cartopy.crs as ccrs

this_dir = os.path.dirname(__file__)
test_dir = os.path.join(this_dir, '../..', 'tests')
data_path = os.path.join(test_dir, 'test_data')
out_path = os.path.join(test_dir, 'test_results')

if not os.path.isdir(out_path):
    os.mkdir(out_path)

testfiles = {'ISMN-6':
                '6-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-ESA_CCI_SM_combined.sm_with_5-SMOS.Soil_Moisture.nc',
             'ISMN-3':
                '3-ISMN.soil moisture_with_1-C3S.sm_with_2-ESA_CCI_SM_combined.sm.nc',
             'GLDAS-6':
                 '6-GLDAS.SoilMoi0_10cm_inst_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-ESA_CCI_SM_combined.sm_with_5-SMOS.Soil_Moisture.nc',
             'GLDAS-3':
                 '3-GLDAS.SoilMoi0_10cm_inst_with_1-C3S.sm_with_2-ESA_CCI_SM_combined.sm.nc'
             }

## === ncplot usecases ===
# ncplot functions use filenames as input and return the filenames to the saved figures.
# === simple boxplot ===
def nc_simple_boxplot():
    import os
    from qa4sm_reader import ncplot
    infile = os.path.join(data_path, testfiles['GLDAS-3'])
    ncplot.boxplot(infile, 'ubRMSD', out_dir=out_path)  # stores a boxplot showing the metric 'ubRMSD' as png.


# === all mapplots of one metric ===
# plot an overview map for each variable
def nc_all_mapplots():
    import os
    from qa4sm_reader import ncplot
    infile = os.path.join(data_path, testfiles['GLDAS-3'])
    for variable in ncplot.get_variables(infile, 'ubRMSD'):  # loop over all variables containing the metric 'ubRMSD'
        ncplot.mapplot(infile, variable, out_dir=out_path)


# === Using qa4sm_reader to generate plots for qa4sm service - the easy way, but loading data twice ===
def nc_qa4sm_integration():
    import logging

    import re
    from os import path, remove
    from zipfile import ZipFile, ZIP_DEFLATED

    import matplotlib.pyplot as plt
    from qa4sm_reader import ncplot, dfplot

    __logger = logging.getLogger(__name__)

    def write_to_zip(myzip, png_filename, svg_filename):
        arcname = path.basename(png_filename)
        myzip.write(png_filename, arcname=arcname)
        arcname = path.basename(svg_filename)
        myzip.write(svg_filename, arcname=arcname)
        remove(svg_filename)  # we don't need the vector image anywhere but in the zip

    def generate_all_graphs(validataion_run, outfolder):
        if not validation_run.output_file:
            return None

        zipfilename = path.join(outfolder, 'graphs.zip')
        __logger.debug('Trying to create zipfile {}'.format(zipfilename))

        filepath = validation_run.output_file.path  # get filepath from validation run object

        with ZipFile(zipfilename, 'w', ZIP_DEFLATED) as myzip:
            for metric in ncplot.get_metrics(filepath):  # loop over available metrics
                [png_filename, svg_filename] = ncplot.boxplot(filepath, metric, out_dir=out_path, out_type=['png', 'svg'])
                write_to_zip(myzip, png_filename, svg_filename)
                for var in ncplot.get_variables(filepath, metric):
                    [png_filename, svg_filename] = ncplot.mapplot(filepath, var, out_dir=out_path,
                                                                  out_type=['png', 'svg'])
                    write_to_zip(myzip, png_filename, svg_filename)


## === dfplot usecases ===
# === Using qa4sm_reader to generate plots for qa4sm service - the hard way, but loading data only once ===
def df_qa4sm_integration():
    import logging

    import re
    from os import path, remove
    from zipfile import ZipFile, ZIP_DEFLATED

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
                df, varmeta = qa4sm_reader.read.load(filepath, metric)
                # df is a pandas.DataFrame containing the variables and lat/lon as rows.
                # varmeta is a dict, containing the variables as keys and a metadata dictionary as values.

                # === boxplot ===
                fig, ax = qa4sm_reader.plot.boxplot(df, varmeta)

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

                for var in varmeta:  # ncplot.get_variables(filepath, metric):
                    # === plot ===
                    fig, ax = qa4sm_reader.plot.mapplot(df, var=var, meta=varmeta[var])

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
