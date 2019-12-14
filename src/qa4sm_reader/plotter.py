# -*- coding: utf-8 -*-

"""
Module description
"""
# TODO:
#   (+) 
#---------
# NOTES:
#   -
from src.qa4sm_reader.img import QA4SMImg
import os
from qa4sm_reader import globals
import numpy as np

class QA4SMBoxPlotter(object):

    def __init__(self, image):
        """
        Create box plots from results in a qa4sm output file.

        Parameters
        ----------
        image : QA4SMImg
            The results object.
        """
        self.img = image


    def _title_basic(self, metric_meta, max_len=100):
        ref_parts = [contributing_datasets['ref']['pretty_name'],
                     contributing_datasets['ref']['pretty_version']]
        ds_parts = []
        for ds in contributing_datasets['dss']:
            ds_parts.append('{} ({})'.format(ds['pretty_name'], ds['pretty_version']))

        title_ref_part = 'Comparing {0} ({1}) to '.format(ref_parts[0], ref_parts[1])

        title = ''
        parts = [title_ref_part] + ds_parts
        for i, part in enumerate(parts):
            if i > 0 and i < len(parts)-1 :
                part = part + ' and '
            if len(title.split('\n')[-1]) + len(part) > max_len:
                part += '\n'
            title = title + part

        return title

    def boxplot_basic(self, metric, out_dir=None, out_name=None, out_type=None):
        """
        Creates a boxplot, displaying the variables corresponding to given metric.
        Saves a figure and returns Matplotlib fig and ax objects for further processing.

        Parameters
        ----------
        metric : str
            metric that is collected from the file for all datasets and combined
            into one plot.
        out_dir : str, optional (default: None)
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
        df = self.metric_df(metric)
        metric_meta = self.metric_meta(metric)
        vars = metric_meta.keys()

        # === rename columns = label of boxes ===
        for var in vars:
            contributing_datasets = {
                'ref': metric_meta[var]['ref'][1],
                'dss' : [ds[1] for ds in metric_meta[var]['dss']],
                'mds': metric_meta[var]['mds'][1] if metric_meta[var]['mds'] is not None else None}

            if metric in globals.metric_groups[0]:
                ds_part = 'All datasets'
            else:
                ds_parts = []
                for i, ds in contributing_datasets['dss'].items():
                    ds_parts.append('{}\n({})'.format(ds['pretty_name'], ds['pretty_version']))
                ds_part = '\n'.join(ds_parts)

            if globals.boxplot_printnumbers:
                m_part = 'median: {0:.3g}\nstd. dev.: {1:.3g}\nN obs.: {2:d}'.format(
                    df[var].median(),
                    df[var].std(),
                    df[var].count())
                new_name = '{}\n{}'.format(ds_part, m_part)
            else:
                new_name = ds_part
            df = df.rename(columns={var: new_name})

        # === create title ===
        max_title_len = globals.boxplot_title_len * len(df.columns)
        title = self._title_basic(metric_meta, max_title_len)

        # === create label ===
        label = (globals._metric_name[metric] +
                 globals._metric_description[metric].format(
                     globals._metric_units[ref_short_name]))

        figsize = [globals.boxplot_width * (1 + len(df.columns)),
                   globals.boxplot_height]

        # === plot data ===
        fig, ax = boxplot(df=df, label=label, figsize=figsize, dpi=globals.dpi)

        # === set limits ===
        ax.set_ylim(get_value_range(df, metric))

        # === add title ===
        ax.set_title(title, pad=globals.title_pad)

        # === add watermark ===
        if globals.watermark_pos not in [None, False]:
            make_watermark(fig, globals.watermark_pos)
        # === save ===
        if not out_name:
            out_name = 'boxplot_{}'.format(metric)

        if out_dir is None:
            return fig, ax
        else:
            out_dir, out_name, out_type = self._get_dir_name_type(
                out_name, out_type, out_dir)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            for ending in out_type:
                fname = os.path.join(out_dir, out_name+ending)
                plt.savefig(fname, dpi='figure', bbox_inches='tight')
                fnames.append(fname)
            plt.close()
            return fnames