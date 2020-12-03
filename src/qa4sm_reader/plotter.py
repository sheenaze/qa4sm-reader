# -*- coding: utf-8 -*-

from qa4sm_reader.img import QA4SMImg
import os
import seaborn as sns
from qa4sm_reader.plot_utils import *

def _make_cbar(fig, im, cax, ref_short, metric):
    try:
        label = globals._metric_name[metric] + \
                globals._metric_description[metric].format(
                    globals._metric_units[ref_short])
    except KeyError as e:
        raise Exception('The metric \'{}\' or reference \'{}\' is not known.\n'.format(metric, ref_short) + str(e))
    extend = get_extend_cbar(metric)
    cbar = fig.colorbar(im, cax=cax, orientation='horizontal', extend=extend)
    cbar.set_label(label, weight='normal')  # TODO: Bug: If a circumflex ('^') is in the string, it becomes bold.)
    cbar.outline.set_linewidth(0.4)
    cbar.outline.set_edgecolor('black')
    cbar.ax.tick_params(width=0.4)  # , labelsize=4)

    return fig, im, cax

def boxplot(df, label=None, figsize=None, dpi=100):
    """
    Create a boxplot_basic from the variables in df.
    The box shows the quartiles of the dataset while the whiskers extend
    to show the rest of the distribution, except for points that are
    determined to be “outliers” using a method that is a function of
    the inter-quartile range.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing 'lat', 'lon' and (multiple) 'var' Series.
    title : str, optional (default: None)
        Title of the plot. If None, no title is added.
    label : str, optional
        Label of the y axis, describing the metric. If None, a label is autogenerated from metadata.
        The default is None.
    figsize : tuple, optional
        Figure size in inches. The default is globals.map_figsize.
    dpi : int, optional
        Resolution for raster graphic output. The default is globals.dpi.
    title_pad : float, optional
        pad the title by title_pad pt. The default is globals.title_pad.

    Returns
    -------
    fig : TYPE
        DESCRIPTION.
    ax : TYPE
        DESCRIPTION.

    """
    df = df.copy()
    # === plot ===
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax = sns.boxplot(data=df, ax=ax, width=0.15, showfliers=False, color='white')
    sns.despine()  # remove ugly spines (=border around plot) right and top.

    if label is not None:
        ax.set_ylabel(label, weight='normal')  # TODO: Bug: If a circumflex ('^') is in the string, it becomes bold.)

    return fig, ax



def mapplot(df, var, metric, ref_short, ref_grid_stepsize=None, plot_extent=None, colormap=None,
            projection=None, add_cbar=True, figsize=globals.map_figsize, dpi=globals.dpi, **style_kwargs):

        """
        Create an overview map from df using df[var] as color.
        Plots a scatterplot for ISMN and a image plot for other input values.
        Parameters
        ----------
        df: pandas.DataFrame
                DataFrame with lat and lon in the multiindex and var as a column
        var: str
            variable to be plotted.
        metric:
        ref_short: str
                short name of the reference dataset (read from netCDF file)
        ref_is_regular:  bool (or 0, 1), optional (True by default)
                information if dataset hase a regular grid (in terms of angular distance)
        ref_grid_stepsize: float or None, optional (None by default)
                angular grid stepsize, needed only when ref_is_angular == False,
        plot_extent: tuple
                (x_min, x_max, y_min, y_max) in Data coordinates. The default is None.
        colormap:  Colormap, optional
                colormap to be used.
                If None, defaults to globals._colormaps.
        projection:  cartopy.crs, optional
                Projection to be used. If none, defaults to globals.map_projection.
                The default is None.
        add_cbar: bool, optional
                Add a colorbar. The default is True.
        figsize: tuple, optional
            Figure size in inches. The default is globals.map_figsize.
        dpi: int, optional
            Resolution for raster graphic output. The default is globals.dpi.
        style_kwargs:
            Keyword arguments for plotter.style_map().
        Returns
         -------
        fig : TYPE
            DESCRIPTION.
        ax : TYPE
            DESCRIPTION.
        """
    
        # === value range ===

        v_min, v_max = get_value_range(df[var], metric)

        # === init plot ===
        fig, ax, cax = init_plot(figsize, dpi, add_cbar, projection)

        if not colormap:
            # colormap = globals._colormaps[meta['metric']]
            cmap = globals._colormaps[metric]
        else:
            cmap = colormap
        # cmap = plt.cm.get_cmap(colormap)

        # === scatter or mapplot ===
        if ref_short in globals.scattered_datasets:  # === scatterplot ===
            # === coordiniate range ===
            if not plot_extent:
                plot_extent = get_plot_extent(df)

            # === marker size ===
            markersize = globals.markersize ** 2  # in points**2

            # === plot ===
            lat, lon = globals.index_names
            im = ax.scatter(df.index.get_level_values(lon), df.index.get_level_values(lat),
                            c=df[var], cmap=cmap, s=markersize, vmin=v_min, vmax=v_max, edgecolors='black',
                            linewidths=0.1, zorder=2, transform=globals.data_crs)
        else:  # === mapplot ===
            # === coordiniate range ===
            if not plot_extent:
                plot_extent = get_plot_extent(df, grid=True)

            # === prepare values ===
            zz, zz_extent, origin = geotraj_to_geo2d(df, var, grid_stepsize=ref_grid_stepsize)

            # === plot ===
            im = ax.imshow(zz, cmap=cmap, vmin=v_min, vmax=v_max,
                           interpolation='nearest', origin=origin,
                           extent=zz_extent,
                           transform=globals.data_crs, zorder=2)

        # === add colorbar ===
        if add_cbar:
            _make_cbar(fig, im, cax, ref_short, metric)

        style_map(ax, plot_extent, **style_kwargs)

        # === layout ===
        fig.canvas.draw()  # very slow. necessary bcs of a bug in cartopy: https://github.com/SciTools/cartopy/issues/1207
        # plt.tight_layout()  # pad=1)  # pad=0.5,h_pad=1,w_pad=1,rect=(0, 0, 1, 1))
        return fig, ax

def get_dir_name_type(out_name, out_type='png', out_dir=None):
    """
    Standardized behaviour for filenames.

    Parameters
    ----------

    out_name : str
        output filename.
        if it contains an extension (e.g. 'MyName.png'), the extension is added to out_ext.
    out_type : str or iterable, optional (default: None)
        contains file extensions to be plotted.
        if None, '.png' is used. If '.' is missing, it is added.
    out_dir : str, optional (default: None)
        path to the output directory.
        if None, uses the current working directory.

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

class QA4SMPlotter(object):

    def __init__(self, image, out_dir=None):
        """
        Create box plots from results in a qa4sm output file.

        Parameters
        ----------
        image : QA4SMImg
            The results object.
        out_dir : str, optional (default: None)
            Path to output generated plot.
            If None, defaults to the current working directory.
            The default is None.
        """
        self.img = image
        self.out_dir = out_dir

    def _box_stats(self, ds:pd.Series, med:bool=True, std:bool=True,
                   count:bool=True) -> str:
        """ Create the metric part with stats of the box caption """

        std = ds.std() if std else None
        count = ds.count() if count else None

        met_str = []
        if med:
            met_str.append('median: {:.3g}'.format(ds.median()))
        if std:
            met_str.append('std. dev.: {:.3g}'.format(ds.std()))
        if count:
            met_str.append('N: {:d}'.format(ds.count()))

        return '\n'.join(met_str)

    def _box_caption(self, dss_meta, ignore_ds_idx:list=None, caption_header=None) -> str:
        """ Create the dataset part of the box caption """

        ds_parts = []
        for i, ds_meta in dss_meta: # [(1, {meta})]
            if (ignore_ds_idx is not None) and (i in ignore_ds_idx):
                continue
            ds_parts.append('{0}\n({1})'.format(ds_meta['pretty_name'],
                                                ds_meta['pretty_version']))

        ds_part = '\n and \n'.join(ds_parts)

        if caption_header is not None:
            ds_part = caption_header + '\n' + ds_part

        return ds_part

    def _comb_title_parts(self, title_parts, max_len) -> str:
        title = ''
        for i, part in enumerate(title_parts):
            if len(title.split('\n')[-1]) + len(part) > max_len:
                part += '\n'
            title = title + part
        if title[-1:] == '\n':
            title = title[:-1]
        return title

    def _box_title_tc(self, ref_meta:dict, mds_meta:dict, metric:str,
                         max_len=100) -> str:
        """ Create the plot title for tc metrics """

        ref_parts = [ref_meta['pretty_name'], ref_meta['pretty_version']]
        met_parts = [mds_meta['pretty_name'], mds_meta['pretty_version']]
        metric_pretty = globals._metric_name[metric]

        title_parts = ['Intercomparison of ',  '{} '.format(metric_pretty),
                       'for {0} ({1}) '.format(met_parts[0], met_parts[1]),
                       'with {0} ({1}) '.format(ref_parts[0], ref_parts[1]),
                       'as the reference']

        return self._comb_title_parts(title_parts, max_len)


    def _box_title_basic(self, ref_meta:dict, metric:str, max_len=100) -> str:
        """ Create the plot title for basic metrics (common and double) """

        ref_parts = [ref_meta['pretty_name'], ref_meta['pretty_version']]
        metric_pretty = globals._metric_name[metric]

        title_parts = ['Intercomparison of ',  '{} '.format(metric_pretty),
                       'with {0} ({1}) '.format(ref_parts[0], ref_parts[1]),
                       'as the reference']

        return self._comb_title_parts(title_parts, max_len)

    def _map_title_basic(self, ref_meta:dict, ds_meta:dict, metric:str,
                         max_len:int=100) -> str:
        """ Create the plot title for basic metrics (common and double) """

        ref_parts = [ref_meta['pretty_name'], ref_meta['pretty_version']]
        ds_parts = [ds_meta['pretty_name'], ds_meta['pretty_version']]

        metric_pretty = globals._metric_name[metric]

        title_parts = ['{} '.format(metric_pretty),
                       'for {0} ({1}) '.format(ds_parts[0], ds_parts[1]),
                       'with {0} ({1}) '.format(ref_parts[0], ref_parts[1]),
                       'as the reference']

        return self._comb_title_parts(title_parts, max_len)

    def _map_title_tc(self, ref_meta:dict, ds_meta:dict, ds2_meta:dict,
                      met_meta:dict, metric:str, max_len:int=100) -> str:
        """ Create the plot title for basic metrics (common and double) """

        ref_parts = [ref_meta['pretty_name'], ref_meta['pretty_version']]
        ds_parts = [ds_meta['pretty_name'], ds_meta['pretty_version']]
        ds2_parts = [ds2_meta['pretty_name'], ds2_meta['pretty_version']]
        met_parts = [met_meta['pretty_name'], met_meta['pretty_version']]
        other_parts = [ds_parts[0] if ds_parts[0] != met_parts[0] else ds2_parts[0],
                      ds_parts[1] if ds_parts[1] != met_parts[1] else ds2_parts[1]]

        metric_pretty = globals._metric_name[metric]

        title_parts = ['{} '.format(metric_pretty),
                       'for {0} ({1}) '.format(met_parts[0], met_parts[1]),
                       'with {0} ({1}) '.format(other_parts[0], other_parts[1]),
                       'and {0} ({1}) '.format(ref_parts[0], ref_parts[1]),
                       'as the reference']

        return self._comb_title_parts(title_parts, max_len)


    def boxplot_tc(self, metric, out_type=None,
                      add_stats=globals.boxplot_printnumbers):
        """

        """
        fnames = list()  # list to store all filenames.

        # === load values and metadata ===
        dfs = self.img.metric_df(metric)
        for i, df in enumerate(dfs):
            tcvars = df.columns.values
            REF_META, _, MDS_META = self.img.var_meta(tcvars[0])[metric]
            for tcvar in tcvars:
                ref_meta, dss_meta, mds_meta = self.img.var_meta(tcvar)[metric]
                assert mds_meta == MDS_META
                assert ref_meta == REF_META

                box_cap_ds = self._box_caption(
                    dss_meta, ignore_ds_idx=[mds_meta[0], ref_meta[0]],
                    caption_header='Other Data:')

                if add_stats:
                    box_stats = self._box_stats(df[tcvar])
                    box_cap = '{}\n{}'.format(box_cap_ds, box_stats)
                else:
                    box_cap = box_cap_ds

                df = df.rename(columns={tcvar: box_cap})

            max_title_len = globals.boxplot_title_len * len(df.columns)
            title = self._box_title_tc(REF_META[1], MDS_META[1], metric, max_title_len)

            # === create label ===
            mds_label = ' for {} ({})'.format(MDS_META[1]['pretty_name'],
                                          MDS_META[1]['pretty_version'])
            label = (globals._metric_name[metric] + mds_label +
                     globals._metric_description[metric].format(
                         globals._metric_units[REF_META[1]['short_name']]))

            # === plot values ===
            figwidth = globals.boxplot_width * (1 + len(df.columns))
            figsize = [figwidth, globals.boxplot_height]

            fig, ax = boxplot(df=df, label=label, figsize=figsize, dpi=globals.dpi)

            # === set limits ===
            ##ax.set_ylim(get_value_range(df, metric))

            # === add title ===
            ax.set_title(title, pad=globals.title_pad)

            # === add watermark ===
            if globals.watermark_pos not in [None, False]:
                make_watermark(fig, globals.watermark_pos, offset=0.1)

            # === save ===
            out_name = 'boxplot_{}_for_{}-{}'.format(metric, MDS_META[0], MDS_META[1]['short_name'])

            out_dir, out_name, out_type = get_dir_name_type(out_name, out_type, self.out_dir)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            for ending in out_type:
                fname = os.path.join(out_dir, out_name+ending)
                if os.path.isfile(fname):
                    warnings.warn('Overwriting file {}'.format(fname))
                plt.savefig(fname, dpi='figure', bbox_inches='tight')
                fnames.append(fname)
            plt.close()
        return fnames

    def boxplot_basic(self, metric, out_name=None, out_type=None,
                      add_stats=globals.boxplot_printnumbers):
        """
        Creates a boxplot_basic, displaying the variables corresponding to given metric.
        Saves a figure and returns Matplotlib fig and ax objects for further processing.

        Parameters
        ----------
        metric : str
            metric that is collected from the file for all datasets and combined
            into one plot.
        out_name : [ None | str ], optional
            Name of output file.
            If None, defaults to a name that is generated based on the variables.
            The default is None.
        out_type : [ str | list | None ], optional
            The file type, e.g. 'png', 'pdf', 'svg', 'tiff'...
            If list, a plot is saved for each type.
            If None, no file is saved.
            The default is png.
        add_stats : bool, optional (default: from globals)
            Add stats of median, std and N to the box bottom.

        Returns
        -------
        fig : matplotlib.figure.Figure
            Figure containing the axes for further processing.
        ax : matplotlib.axes.Axes or list of Axes objects
            Axes or list of axes containing the plot.
        """
        fnames = list()  # list to store all filenames.

        # === load values and metadata ===
        df = self.img.metric_df(metric)
        metric_meta = self.img.metric_meta(metric)
        ref_meta = self.img.ref_meta()[1]

        # === rename columns = label of boxes ===
        for var, meta in metric_meta.items():
            dss_meta = meta[1]

            if var in self.img.ls_vars(True)['common']:
                box_cap_ds = 'All datasets'
            else:
                box_cap_ds = self._box_caption(dss_meta)
            if add_stats:
                box_stats = self._box_stats(df[var])
                box_cap = '{}\n{}'.format(box_cap_ds, box_stats)
            else:
                box_cap = box_cap_ds

            df = df.rename(columns={var: box_cap})

        # === create title ===
        max_title_len = globals.boxplot_title_len * len(df.columns)
        title = self._box_title_basic(ref_meta, metric, max_title_len)

        # === create label ===
        label = (globals._metric_name[metric] +
                 globals._metric_description[metric].format(
                     globals._metric_units[ref_meta['short_name']]))

        # === plot values ===
        figwidth = globals.boxplot_width * (1 + len(df.columns))
        figsize = [figwidth, globals.boxplot_height]

        fig, ax = boxplot(df=df, label=label, figsize=figsize, dpi=globals.dpi)

        # === set limits ===
        #ax.set_ylim(get_value_range(df, metric))

        # === add title ===
        ax.set_title(title, pad=globals.title_pad)

        # === add watermark ===
        if globals.watermark_pos not in [None, False]:
            make_watermark(fig, globals.watermark_pos)

        # === save ===
        if not out_name:
            out_name = 'boxplot_{}'.format(metric)

        if self.out_dir is None:
            return fig, ax
        else:
            out_dir, out_name, out_type = get_dir_name_type(out_name, out_type, self.out_dir)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            for ending in out_type:
                fname = os.path.join(out_dir, out_name+ending)
                plt.savefig(fname, dpi='figure', bbox_inches='tight')
                fnames.append(fname)
            plt.close('all')
            return fnames

    def mapplot_var(self, varname, out_name=None, out_type=None,
                **plot_kwargs):
        """
        Plots values to a map, using the values as color. Plots a scatterplot for
        ISMN and a image plot for other input values.

        Parameters
        ----------
        filepath : str
            Path to the *.nc file to be processed.
        varname : str
            Name of a variable in the image to make the map for.
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
        df = self.img._ds2df([varname])
        var_meta = self.img.var_meta(varname)

        assert len(list(var_meta.keys())) == 1
        metric = list(var_meta.keys())[0]

        ref_short = self.img.ref_dataset
        ref_grid_stepsize = self.img.ref_dataset_grid_stepsize

        # === plot values ===
        fig, ax = mapplot(df=df, var=varname, metric=metric, ref_short=ref_short, ref_grid_stepsize = ref_grid_stepsize,
                          plot_extent=self.img.extent, **plot_kwargs)

        # === add title ===
        if var_meta[metric][1] is None:
            title_parts = ['{} '.format(globals._metric_name[metric]),
                           'between all datasets']
            title = self._comb_title_parts(title_parts, globals.max_title_len)
        else:
            if metric in globals.metric_groups[3]:
                title = self._map_title_tc(ref_meta=var_meta[metric][0][1],
                                           ds_meta=var_meta[metric][1][0][1],
                                           ds2_meta=var_meta[metric][1][1][1],
                                           met_meta=var_meta[metric][2][1],
                                           metric=metric,
                                           max_len=globals.max_title_len)
            else:
                title = self._map_title_basic(ref_meta=var_meta[metric][0][1],
                                              ds_meta=var_meta[metric][1][0][1],
                                              metric=metric, max_len=globals.max_title_len)
        ax.set_title(title, pad=globals.title_pad)

        # === add watermark ===
        if globals.watermark_pos not in [None, False]:
            make_watermark(fig, globals.watermark_pos, for_map=True)
        # === save ===
        if not out_name:
            ref_num = var_meta[metric][0][0]
            if metric in globals.metric_groups[0]:
                out_name = 'overview_{}'.format(varname)
            elif metric in globals.metric_groups[2]:
                ds_meta = var_meta[metric][1][0]
                out_name = 'overview_{}-{}_and_{}-{}_{}'.format(
                    ref_num, ref_short, ds_meta[0], ds_meta[1]['short_name'], metric)
            else:
                ds_meta = var_meta[metric][1][0]
                ds2_meta = var_meta[metric][1][1]
                met_meta = var_meta[metric][2]
                out_name = 'overview_{}-{}_and_{}-{}_and_{}-{}_{}_for_{}-{}'.format(
                    ref_num, ref_short, ds_meta[0], ds_meta[1]['short_name'], ds2_meta[0],
                    ds2_meta[1]['short_name'], metric, met_meta[0], met_meta[1]['short_name'])


        if self.out_dir is None:
            return fig, ax
        else:
            fnames = []
            out_dir, out_name, out_type = \
                get_dir_name_type(out_name, out_type, self.out_dir)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            for ending in out_type:
                fname = os.path.join(out_dir, out_name+ending)
                plt.savefig(fname, dpi='figure', bbox_inches='tight')
                fnames.append(fname)
            plt.close('all')
            return fnames

    def mapplot(self, metric, out_type=None, **plot_kwargs):
        """
        Plot ALL variables for a given metric in the loaded file.

        Parameters
        ----------
        filepath : str
            Path to the *.nc file to be processed.
        metric : str
            Name of a metric. File is searched for variables for that metric.
        **kwargs : dict, optional
            Additional keyword arguments that are passed to mapplot_var

        Returns
        -------
        fnames : list
            List of files that were created
        """

        varnames = list(self.img.metric_meta(metric).keys())
        fnames = []
        for varname in varnames:
            fns = self.mapplot_var(varname, out_name=None, out_type=out_type, **plot_kwargs)
            plt.close('all')
            for fn in fns: fnames.append(fn)
        return fnames
