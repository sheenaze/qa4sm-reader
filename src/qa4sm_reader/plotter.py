# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt
import os
import re

from qa4sm_reader.plot import mapplot, boxplot
from qa4sm_reader.read import QA4SM_MetaImg


class QA4SM_MetaImg_Plotter(QA4SM_MetaImg):
    def __init__(self, filepath):
        super(QA4SM_MetaImg_Plotter, self).__init__(filepath)

    @staticmethod
    def _get_dir_name_type(out_dir, out_name, out_type):
        """
        Standardized behaviour for filenames.

        Parameters
        ----------
        out_dir : [ str | None ]
            path to the output directory.
            if None, uses the current working directory.
        out_name : str
            output filename.
            if it contains an extension (e.g. 'MyName.png'), the extension is added to out_ext.
        out_type : [ str | iterable | None ]
            contains file extensions to be plotted.
            if None, '.png' is used. If '.' is missing, it is added.

        Returns
        -------
        out_dir : str
        out_name : str
        out_ext : set
            file extensions

        """
        # directory
        if not out_dir:
            out_dir = ''
        out_dir = os.path.abspath(out_dir)
        # file name
        (out_name, ext) = os.path.splitext(out_name)  # remove extension
        # file type
        if not out_type:
            if ext:
                out_type = ext
            else:
                out_type = '.png'
        # convert to a set
        if isinstance(out_type, str):
            out_type = {out_type}
        else:  # some iterable
            out_type = set(out_type)
        if ext:
            out_type.add(ext)
        out_type = {ext if ext[0] == "." else "." + ext for ext in out_type}  # make sure all entries start with a '.'
        return out_dir, out_name, out_type

    def boxplot(self, metric, extent=None, out_dir=None, out_name=None, out_type=None,
                **plot_kwargs):
        """
        Creates a boxplot, displaying the variables corresponding to given metric.
        Saves a figure and returns Matplotlib fig and ax objects for further processing.

        Parameters
        ----------
        filepath : str
            Path to the *.nc file to be processed.
        metric : str of list of str
            metric to be plotted.
            alternatively a list of variables can be given.
        extent : list
            [x_min,x_max,y_min,y_max] to create a subset of the data
        out_dir : [ None | str ], optional
            Path to output generated plot.
            If None, defaults to the current working directory.
            The default is None.
        out_name : [ None | str ], optional
            Name of output file.
            If None, defaults to a name that is generated based on the variables.
            The default is None.
        out_type : [ str | list | None ], optional
            The file type, e.g. 'png', 'pdf', 'svg', 'tiff'...
            If list, a plot is saved for each type.
            If None, no file is saved.
            The default is png.
        **plot_kwargs : dict, optional
            Additional keyword arguments that are passed to dfplot.boxplot.

        Returns
        -------
        fig : matplotlib.figure.Figure
            Figure containing the axes for further processing.
        ax : matplotlib.axes.Axes or list of Axes objects
            Axes or list of axes containing the plot.

        """
        fnames = list()  # list to store all filenames.
        # === load data and metadata ===
        df, varmeta = self._ds2df(self._vars4metric(metric), extent)

        # === plot data ===
        fig, ax = boxplot(df=df, varmeta=varmeta, **plot_kwargs)

        # === save ===
        if not out_name:
            out_name = 'boxplot_{}'.format(metric)
        out_dir, out_name, out_type = self._get_dir_name_type(out_dir, out_name,
                                                              out_type)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for ending in out_type:
            fname = os.path.join(out_dir, out_name+ending)
            plt.savefig(fname, dpi='figure')
            fnames.append(fname)
        plt.close()
        return fnames


    def mapplot(self, var, extent=None, out_dir=None, out_name=None, out_type=None,
                **plot_kwargs):
        """
        Plots data to a map, using the data as color. Plots a scatterplot for
        ISMN and a image plot for other input data.

        Parameters
        ----------
        filepath : str
            Path to the *.nc file to be processed.
        var : [ str | list ]
            variable to be plotted.
        extent : list
            [x_min,x_max,y_min,y_max] to create a subset of the data
        out_dir : [ None | str ], optional
            Path to output generated plot.
            If None, defaults to the current working directory.
            The default is None.
        out_name : [ None | str ], optional
            Name of output file.
            If None, defaults to a name that is generated based on the variables.
            The default is None.
        out_type : [ str | list | None ], optional
            The file type, e.g. 'png', 'pdf', 'svg', 'tiff'...
            If list, a plot is saved for each type.
            If None, no file is saved.
            The default is png.
        **plot_kwargs : dict, optional
            Additional keyword arguments that are passed to dfplot.

        Returns
        -------
        fig : matplotlib.figure.Figure
            Figure containing the axes for further processing.
        ax : matplotlib.axes.Axes or list of Axes objects
            Axes or list of axes containing the plot.

        """
        fnames = list()  # list to store all filenames.

        if isinstance(var, str):
            variables = [var]  # raise IOError('var needs to be a string, not {}.'.format(type(var)))

        # === Get ready... ===
        df, varmeta = self._ds2df(var, extent)

        for var in varmeta:  # plot all specified variables (usually only one)
            meta = varmeta[var]
            # === plot data ===
            fig, ax = mapplot(df=df, var=var, meta=meta, **plot_kwargs)

            # === save ===
            if not out_name:
                ds_match = re.match(r'.*_between_(([0-9]+)-(.*)_([0-9]+)-(.*))', var)
                if ds_match:
                    pair_name = ds_match.group(1)
                else:
                    pair_name = var  # e.g. n_obs

                if meta['metric'] == pair_name:  # e.g. n_obs
                    out_name = 'overview_{}'.format(meta['metric'])
                else:
                    out_name = 'overview_{}_{}'.format(pair_name, meta['metric'])
            out_dir, out_name, out_type = self._get_dir_name_type(out_dir, out_name, out_type)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            for ending in out_type:
                fname = os.path.join(out_dir, out_name+ending)
                plt.savefig(fname, dpi='figure')
                fnames.append(fname)
            plt.close()
        return fnames

if __name__ == '__main__':
    afile = r"H:\code\qa4sm-reader\tests\test_data\3-GLDAS.SoilMoi0_10cm_inst_with_1-C3S.sm_with_2-ESA_CCI_SM_combined.sm.nc"
    plotter = QA4SM_MetaImg_Plotter(afile)
    out_dir = r"C:\Temp\qa4smreader_plots"
    plotter.boxplot('R', out_dir=out_dir)