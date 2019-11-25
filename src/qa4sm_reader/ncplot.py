# -*- coding: utf-8 -*-
import qa4sm_reader.plot

__author__ = "Lukas Racbhauer"
__copyright__ = "2019, TU Wien, Department of Geodesy and Geoinformation"
__license__ = "mit"


"""
Contains an interface for opening QA4SM output files (*.nc), 
loading certain parts as pandas.DataFrame 
and producing plots using the dfplot module in this package.

naming convention:
------------------
filepath : str
    Path to the *.nc file to be processed.
metric : str
    metric to be plotted.
metrics : list
    list of [metric]
var : str
    variable to be plotted.
variables : list
    list of [var]
meta : dict
    dictionary containing metadata for one var
varmeta : dict
    dictionary containing {var : meta}
    
Internally, xarray is used to open the NetCDF files.
"""

from qa4sm_reader import globals
import xarray as xr
import matplotlib.pyplot as plt
import re
import os
#from qa4sm_reader.read import load, _get_var, _get_varmeta, _get_meta


# === File level ===

def get_metrics(filepath):
    "Returns a list of metrics available in the current filepath"
    with xr.open_dataset(filepath) as ds:
        metrics = _get_metrics(ds)
    return metrics


def _get_metrics(ds):
    varmeta = _get_varmeta(ds)
    return {varmeta[meta]['metric'] for meta in varmeta}


def plot_all(filepath, metrics=None, extent=None, out_dir=None, out_type='png', boxplot_kwargs=dict(),
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
    fnames = list()  # list to store all filenames.

    if not out_dir:
        out_dir = os.path.join(os.getcwd(), os.path.basename(filepath))

    # === Metadata ===
    if not metrics:
        metrics = get_metrics(filepath)

    for metric in metrics:
        # === load data and metadata ===
        df, varmeta = load(filepath, metric, extent)

        # === boxplot ===
        fig, ax = qa4sm_reader.plot.boxplot(df, varmeta, **boxplot_kwargs)

        # === save ===
        curr_dir = os.path.join(out_dir, metric)
        out_name = 'boxplot_{}'.format(metric)
        curr_dir, out_name, out_type = _get_dir_name_type(curr_dir, out_name, out_type)
        if not os.path.exists(curr_dir):
            os.makedirs(curr_dir)
        for ending in out_type:
            fname = os.path.join(curr_dir, out_name+ending)
            plt.savefig(fname, dpi='figure')
            fnames.append(fname)

        plt.close()

        # === mapplot ===
        for var in varmeta:
            meta = varmeta[var]
            # === plot ===
            fig, ax = qa4sm_reader.plot.mapplot(df, var=var, meta=meta, **mapplot_kwargs)

            # === save ===
            ds_match = re.match(r'.*_between_(([0-9]+)-(.*)_([0-9]+)-(.*))', var)
            if ds_match:
                pair_name = ds_match.group(1)
            else:
                pair_name = var  # e.g. n_obs

            if metric == pair_name:  # e.g. n_obs
                out_name = 'overview_{}'.format(metric)
            else:
                out_name = 'overview_{}_{}'.format(pair_name, metric)

            for ending in out_type:
                fname = os.path.join(curr_dir, out_name+ending)
                plt.savefig(fname, dpi='figure')
                fnames.append(fname)

            plt.close()

    return fnames


def boxplot(filepath, metric, extent=None, out_dir=None, out_name=None, out_type=None,
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
    df, varmeta = load(filepath, metric, extent)

    # === plot data ===
    fig, ax = qa4sm_reader.plot.boxplot(df=df, varmeta=varmeta, **plot_kwargs)

    # === save ===
    if not out_name:
        out_name = 'boxplot_{}'.format(metric)
    out_dir, out_name, out_type = _get_dir_name_type(out_dir, out_name, out_type)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for ending in out_type:
        fname = os.path.join(out_dir, out_name+ending)
        plt.savefig(fname, dpi='figure')
        fnames.append(fname)
    plt.close()
    return fnames


def mapplot(filepath, var, extent=None, out_dir=None, out_name=None, out_type=None,
            **plot_kwargs):
    """
    Plots data to a map, using the data as color. Plots a scatterplot for ISMN and a image plot for other input data.

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
    df, varmeta = load(filepath, variables, extent)

    for var in varmeta:  # plot all specified variables (usually only one)
        meta = varmeta[var]
        # === plot data ===
        fig, ax = qa4sm_reader.plot.mapplot(df=df, var=var, meta=meta, **plot_kwargs)

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
        out_dir, out_name, out_type = _get_dir_name_type(out_dir, out_name, out_type)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for ending in out_type:
            fname = os.path.join(out_dir, out_name+ending)
            plt.savefig(fname, dpi='figure')
            fnames.append(fname)
        plt.close()
    return fnames


def get_variables(filepath, metric=None):
    """
    Searches the dataset for variables that contain a 'metric_between' and returns a list of strings.
    Drops vars that contain only nan or null values.

    Parameters
    ----------
    filepath : str
    metric : str

    Returns
    -------
    vars : list
    """
    with xr.open_dataset(filepath) as ds:
        variables = _get_var(ds, metric)
    return variables


def get_meta(filepath, var):
    """
    parses the var name and gets metadata from tha *.nc dataset.
    checks consistency between the dataset and the variable name.
    """
    with xr.open_dataset(filepath) as ds:
        return _get_meta(ds, var)


def _get_pretty_name(ds, name, number):
    """
    Returns pretty_name, version and version_pretty_name.
    First tries to find info from ds.attrs.
    Then falls back to globals.
    Then falls back to using name as pretty name.
    """
    try:
        pretty_name = ds.attrs['val_dc_pretty_name' + str(number - 1)]
    except KeyError:
        try:
            pretty_name = globals._dataset_pretty_names[name]
        except KeyError:
            pretty_name = name
    try:
        version = ds.attrs['val_dc_version' + str(number - 1)]
        try:
            version_pretty_name = ds.attrs['val_dc_version_pretty_name' + str(number - 1)]
        except KeyError:
            try:
                version_pretty_name = globals._dataset_version_pretty_names[version]
            except KeyError:
                version_pretty_name = version
    except KeyError:
        version = 'unknown'
        version_pretty_name = 'unknown version'
    return pretty_name, version, version_pretty_name


def get_varmeta(filepath, variables=None):
    """
    get meta for all variables and return a nested dict.
    """
    with xr.open_dataset(filepath) as ds:
        return _get_varmeta(ds, variables)


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
