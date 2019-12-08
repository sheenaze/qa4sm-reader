# -*- coding: utf-8 -*-
import os
import re

from matplotlib import pyplot as plt

import qa4sm_reader.plotter
from qa4sm_reader.plotter import QA4SM_MetaImg_Plotter

def plot_all(filepath, metrics=None, extent=None, out_dir=None, out_type='png',
             boxplot_kwargs=dict(),
             mapplot_kwargs=dict()):
    """
    Creates boxplots for all metrics and map plots for all variables. Saves the output in a folder-structure.

    Parameters
    ----------
    filepath : str
        Path to the *.nc file to be processed.
    metrics : set or list
        metrics to be plotted.
    extent : list
        [x_min,x_max,y_min,y_max] to create a subset of the data
    out_dir : [ None | str ], optional
        Parrent directory where to generate the folder structure for all plots.
        If None, defaults to the current working directory.
        The default is None.
    out_type : [ str | list | None ], optional
        The file type, e.g. 'png', 'pdf', 'svg', 'tiff'...
        If list, a plot is saved for each type.
        If None, no file is saved.
        The default is png.
    **plot_kwargs : dict, optional
        Additional keyword arguments that are passed to dfplot.
    """
    #fnames = list()  # list to store all filenames.

    if not out_dir:
        out_dir = os.path.join(os.getcwd(), os.path.basename(filepath))

    plotter = QA4SM_MetaImg_Plotter(filepath)
    # === Metadata ===
    if not metrics:
        metrics = plotter.metrics_in_file(group=False)

    for metric in metrics:
        # === load data and metadata ===
        plotter.boxplot(metric, extent, out_dir=out_dir, out_type=out_type,
                        **boxplot_kwargs)
        vars = plotter._met2vars(metric)
        for var in vars:
            plotter.mapplot(var, extent, out_dir=out_dir, out_type=out_type,
                            **mapplot_kwargs)
        # df, varmeta = img.load_metric_and_meta(metric, extent)
        #
        # # === boxplot ===
        # plotter.boxplot(metric, extent, out_dir=out_dir)
        #
        # # === save ===
        # curr_dir = os.path.join(out_dir, metric)
        # out_name = 'boxplot_{}'.format(metric)
        # curr_dir, out_name, out_type = _get_dir_name_type(curr_dir, out_name,
        #                                                   out_type)
        # if not os.path.exists(curr_dir):
        #     os.makedirs(curr_dir)
        # for ending in out_type:
        #     fname = os.path.join(curr_dir, out_name+ending)
        #     plt.savefig(fname, dpi='figure')
        #     fnames.append(fname)
        #
        # plt.close()
        #
        # # === mapplot ===
        # for var in varmeta:
        #     meta = varmeta[var]
        #     # === plot ===
        #     fig, ax = qa4sm_reader.plotter.mapplot(df, var=var, meta=meta,
        #                                            **mapplot_kwargs)
        #
        #     # === save ===
        #     ds_match = re.match(r'.*_between_(([0-9]+)-(.*)_([0-9]+)-(.*))', var)
        #     if ds_match:
        #         pair_name = ds_match.group(1)
        #     else:
        #         pair_name = var  # e.g. n_obs
        #
        #     if metric == pair_name:  # e.g. n_obs
        #         out_name = 'overview_{}'.format(metric)
        #     else:
        #         out_name = 'overview_{}_{}'.format(pair_name, metric)
        #
        #     for ending in out_type:
        #         fname = os.path.join(curr_dir, out_name+ending)
        #         plt.savefig(fname, dpi='figure')
        #         fnames.append(fname)
        #
        #     plt.close()

        # return fnames


if __name__ == '__main__':
    afile = '/home/wolfgang/code/qa4sm-reader/tests/test_data/3-GLDAS.SoilMoi0_10cm_inst_with_1-C3S.sm_with_2-ESA_CCI_SM_combined.sm.nc'
    #out_dir = r"C:\Temp\qa4smreader_plots"
    out_dir = r"/tmp/qa4sm_plots"
    plot_all(afile, out_dir=out_dir)
