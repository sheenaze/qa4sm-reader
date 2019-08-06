# -*- coding: utf-8 -*-


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

from qa4sm_reader import dfplot
from qa4sm_reader import globals
import xarray as xr
import matplotlib.pyplot as plt
import re
import os

import warnings

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
    if not out_dir:
        out_dir = os.path.join(os.getcwd(), os.path.basename(filepath))

    # === Metadata ===
    if not metrics:
        metrics = get_metrics(filepath)

    for metric in metrics:
        # === load data and metadata ===
        df, varmeta = load(filepath, metric, extent)

        # === boxplot ===
        fig, ax = dfplot.boxplot(df, varmeta, **boxplot_kwargs)

        # === save ===
        curr_dir = os.path.join(out_dir, metric)
        out_name = 'boxplot_{}'.format(metric)
        curr_dir, out_name, out_type = _get_dir_name_type(curr_dir, out_name, out_type)
        if not os.path.exists(curr_dir):
            os.makedirs(curr_dir)
        for ending in out_type:
            fname = os.path.join(curr_dir, out_name+ending)
            plt.savefig(fname, dpi='figure')
            plt.close()

        # === mapplot ===
        for var in varmeta:
            meta = varmeta[var]
            # === plot ===
            fig, ax = dfplot.mapplot(df, var=var, meta=meta, **mapplot_kwargs)

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
                if out_type:  # don't attempt to save if None.
                    fname = os.path.join(curr_dir, out_name+ending)
                    plt.savefig(fname, dpi='figure')
                    plt.close()


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
    # === load data and metadata ===
    df, varmeta = load(filepath, metric, extent)

    # === plot data ===
    fig, ax = dfplot.boxplot(df=df, varmeta=varmeta, **plot_kwargs)

    # === save ===
    if not out_name:
        out_name = 'boxplot_{}'.format(metric)
    out_dir, out_name, out_type = _get_dir_name_type(out_dir, out_name, out_type)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for ending in out_type:
        fname = os.path.join(out_dir, out_name+ending)
        plt.savefig(fname, dpi='figure')
    plt.close()


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
    if isinstance(var, str):
        variables = [var]  # raise IOError('var needs to be a string, not {}.'.format(type(var)))

    # === Get ready... ===
    df, varmeta = load(filepath, variables, extent)

    for var in varmeta:  # plot all specified variables (usually only one)
        meta = varmeta[var]
        # === plot data ===
        fig, ax = dfplot.mapplot(df=df, var=var, meta=meta, **plot_kwargs)

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
        plt.close()


def load(filepath, metric, extent=None, index_names=globals.index_names):
    """
    Loads data from *.nc file in filepath and returns it as pandas.DataFrame, including a metadata dictionary.

    Parameters
    ----------
    filepath : str
        path to input file
    metric : [ str | list ]
        metric(s) to load
    extent : list, optional
        [lon_min,lon_max,lat_min,lat_max] to create a subset of the data
    index_names : list, optional

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the requested data, stripped by nan values and cropped to extent.
    varmeta : dict
        Dictionary containing a meta dict for each variable in df.
    """
    with xr.open_dataset(filepath) as ds:
        if isinstance(metric, str):
            variables = _get_var(ds, metric)
        elif isinstance(metric, list) or isinstance(metric, set):  # metric is a list and already contais the variables to be plotted.
            variables = metric
        else:
            raise TypeError('The argument metric must be str or list. {} was given.'.format(type(metric)))
        varmeta = _get_varmeta(ds, variables)
        df = _load_data(ds, variables, extent, index_names)
    return df, varmeta


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


def _get_var(ds, metric):
    """"
    Searches the dataset for variables that contain a '<metric>_between' and returns a list of strings.
    Drop vars that contain only nan or null values.
    """
    # TODO: change to set instead of list
    if metric == 'n_obs':  # n_obs is a special case, that does not match the usual pattern with *_between*
        return [metric]
    else:
        variables = [var for var in ds if ~ds[var].isnull().all()]  # reject all nan and null values.
        if metric:  # usual case.
            return [var for var in variables if re.search(r'^{}_between'.format(metric), var, re.I)]  # search for pattern.
        else:  # metric is None, return all variables that contain '_between'
            return [var for var in variables if (re.search(r'_between', var, re.I) or var == 'n_obs')]  # search for pattern.


def load_data(filepath, variables, extent=None, index_names=globals.index_names):
    """
    Loads requested Data from the NetCDF file.

    Parameters
    ----------
    filepath : str
    variables
    extent : list
        [lon_min,lon_max,lat_min,lat_max] to create a subset of the data
    index_names : list [optional]
        defaults to globals.index_names = ['lat', 'lon']

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the requested data.
    """
    with xr.open_dataset(filepath) as ds:
        df = _load_data(ds, variables, extent, index_names)
    return df


def _load_data(ds, variables, extent, index_names):
    """
    converts xarray.DataSet to pandas.DataFrame, reading only relevant variables and multiindex
    """
    if type(variables) is str: variables = [variables]  # convert to list of string
    try:
        df = ds[index_names + variables].to_dataframe()
    except KeyError as e:
        raise Exception(
            'The given variabes ' + ', '.join(variables) + ' do not match the names in the input data.' + str(e))
    df.dropna(axis='index', subset=variables, inplace=True)
    if extent:  # === geographical subset ===
        lat, lon = globals.index_names
        df = df[(df[lon] >= extent[0]) & (df[lon] <= extent[1]) & (df[lat] >= extent[2]) & (df[lat] <= extent[3])]
    df.reset_index(drop=True, inplace=True)
    return df


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


def _get_meta(ds, var):
    """
    parses the var name and gets metadata from tha *.nc dataset.
    checks consistency between the dataset and the variable name.
    """
    # === consistency with dataset ===
    if not var in ds.data_vars:
        raise Exception('The given var \'{}\' is not contained in the dataset.'.format(var))
    # === parse var ===
    meta = dict()
    try:
        pattern = re.compile(
            r"""(\D+)_between_(\d+)-(\S+)_(\d+)-(\S+)""")  # 'ubRMSD_between_4-ISMN_3-ESA_CCI_SM_combined'
        match = pattern.match(var)
        meta['metric'] = match.group(1)
        meta['ref_no'] = int(match.group(2))
        meta['ref'] = match.group(3)
        meta['ds_no'] = int(match.group(4))
        meta['ds'] = match.group(5)
    except AttributeError:
        if var == 'n_obs':  # catch error occurring when var is 'n_obs'
            meta['metric'] = 'n_obs'
            datasets = {}
            i = 1  # numbers as in meta and var. In Attributes, it is numbers-1
            while True:
                try:
                    datasets[i] = ds.attrs['val_dc_dataset' + str(i - 1)]
                    i += 1
                except KeyError:
                    break
            try:
                meta['ref_no'] = int(ds.attrs['val_ref'][-1])  # last character of string is reference number
                meta['ref'] = ds.attrs[ds.attrs['val_ref']]  # e.g. val_ref = "val_dc_dataset3"
            except KeyError:  # for some reason, the attribute lookup failed. Fall back to the last element in dict
                meta['ref_no'] = list(datasets)[-1]
                meta['ref'] = datasets[meta['ref_no']]
            datasets.pop(meta['ref_no'])
            meta['ds_no'] = list(datasets.keys())  # list instead of int
            meta['ds'] = [datasets[i] for i in meta['ds_no']]  # list instead of str
        else:
            raise Exception('The given var \'{}\' does not match the regex pattern.'.format(var))
    # === get pretty names ===
    for i in ('ds', 'ref'):
        name = meta[i]
        number = meta[i + '_no']
        if (type(name) == list) and (
                type(number) == list):  # e.g. ds of n_obs are several: the rest needs to be list as well
            meta[i + '_pretty_name'] = list()
            meta[i + '_version'] = list()
            meta[i + '_version_pretty_name'] = list()
            for na, no in zip(name, number):
                pretty_name, version, version_pretty_name = _get_pretty_name(ds, na, no)
                meta[i + '_pretty_name'].append(pretty_name)
                meta[i + '_version'].append(version)
                meta[i + '_version_pretty_name'].append(version_pretty_name)
        else:  # usual case.
            pretty_name, version, version_pretty_name = _get_pretty_name(ds, name, number)
            meta[i + '_pretty_name'] = pretty_name
            meta[i + '_version'] = version
            meta[i + '_version_pretty_name'] = version_pretty_name
    return meta


def get_varmeta(filepath, variables=None):
    """
    get meta for all variables and return a nested dict.
    """
    with xr.open_dataset(filepath) as ds:
        return _get_varmeta(ds, variables)


def _get_varmeta(ds, variables=None):
    """
    get meta for all variables and return a nested dict.
    """
    if not variables:  # get all variables.
        variables = _get_var(ds, metric=None)
    return {var: _get_meta(ds, var) for var in variables}


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
