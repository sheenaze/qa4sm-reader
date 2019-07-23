# -*- coding: utf-8 -*-
"""
Contains an interface for opening QA4SM output files (*.nc), 
loading certain parts as pandas.DataFrame 
and producing plots using the dfplot module in this package.
Internally, xarray is used to open the NetCDF files.
"""
from qa4smreader import dfplot
from qa4smreader import globals
import xarray as xr
import matplotlib.pyplot as plt
import re
import os

def boxplot(filepath, metric, extent=None, out_dir=None, out_name=None, out_type=None , **plot_kwargs):
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
        If None, defaults to, the input filepath.
        The default is None.
    out_name : [ None | str ], optional
        Name of output file. 
        If None, defaults to a name that is generated based on the variables.
        The default is None.
    out_type : [ None | str ], optional
        The file type, e.g. 'png', 'pdf', 'svg', 'tiff'...
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
    if type(metric) is str:
        variables = get_metric_var(filepath, metric)
    else:
        variables = metric #metric already contais the variables to be plotted.

    # === Get ready... ===
    with xr.open_dataset(filepath) as ds:
        # === Get Metadata ===
        varmeta = _get_varmeta(variables, ds)
        globmeta = _get_globmeta(varmeta)
        # === Load data ===
        df = _load_data(ds, variables, extent, globals.index_names)

    # === plot data ===
    fig,ax = dfplot.boxplot(df=df, varmeta = varmeta, globmeta = globmeta, **plot_kwargs)

    # === save figure ===
    if out_type:
        if not out_dir:
            out_dir = os.path.dirname(__file__)
        if not out_name:
            out_name = 'boxplot_' + '__'.join([var for var in variables])
        filename = os.path.join(out_dir,out_name)
        if type(out_type) is not list: out_type = [out_type]
        for ending in out_type:
            plt.savefig('{}.{}'.format(filename, ending), dpi='figure')
        plt.close()
        return
    elif out_name:
        if out_name.find('.') == -1: #append '.png'out_name contains no '.', which is hopefully followed by a meaningful file ending.
            out_name += '.png'
        filename = os.path.join(out_dir,out_name)
        plt.savefig(filename)
        plt.close()
        return
    else:
        return fig,ax

def mapplot(filepath, var, extent=None, out_dir=None, out_name=None, out_type=None, **plot_kwargs):
    """
    Plots data to a map, using the data as color. Plots a scatterplot for ISMN and a image plot for other input data.
    Saves a figure and returns Matplotlib fig and ax objects for further processing.
    
    Parameters
    ----------
    filepath : str
        Path to the *.nc file to be processed.
    var : str
        variable to be plotted.
    extent : list
        [x_min,x_max,y_min,y_max] to create a subset of the data
    out_dir : [ None | str ], optional
        Path to output generated plot. 
        If None, defaults to, the input filepath.
        The default is None.
    out_name : [ None | str ], optional
        Name of output file. 
        If None, defaults to a name that is generated based on the variables.
        The default is None.
    out_type : [ None | str ], optional
        The file type, e.g. 'png', 'pdf', 'svg', 'tiff'...
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
    #TODO: do something when var is not a string but a list. (e.g. call list plot function)
    if type(var) == list: var = var[0]
    # === Get ready... ===
    with xr.open_dataset(filepath) as ds:
        # === Get Metadata ===
        meta = _get_meta(var, ds)
        # === Load data ===
        df = _load_data(ds, var, extent, globals.index_names)

    # === plot data ===
    if ( meta['ds'] in globals.scattered_datasets or meta['ref'] in globals.scattered_datasets ): #do scatterplot
        fig,ax = dfplot.scatterplot(df=df, var = var, meta = meta, **plot_kwargs)
    else:
        fig,ax = dfplot.mapplot(df=df, var = var, meta = meta, **plot_kwargs)

    # == save figure ===
    if out_type:
        if not out_dir:
            out_dir = os.path.dirname(__file__)
        if not out_name:
            out_name = 'mapplot_' + var
        filename = os.path.join(out_dir,out_name)
        if type(out_type) is not list: out_type = [out_type]
        for ending in out_type:
            plt.savefig('{}.{}'.format(filename, ending), dpi='figure')
    elif out_name:
        if out_name.find('.') == -1: #append '.png'out_name contains no '.', which is hopefully followed by a meaningful file ending.
            out_name += '.png'
        filename = os.path.join(out_dir,out_name)
        plt.savefig(filename, dpi='figure')
    else:
        plt.show()
    plt.close()
    #return fig,ax

def load(filepath, metric, extent=None, index_names=globals.index_names):
    "returns DataFrame, varmeta and globmeta"
    with xr.open_dataset(filepath) as ds:
        variables = _get_metric_var(ds, metric)
        varmeta = _get_varmeta(variables, ds)
        globmeta = _get_globmeta(varmeta)
        df = _load_data(ds, variables, extent, index_names)
    return df, varmeta, globmeta

def get_metric_var(filepath, metric):
    "Searches the dataset for variables that contain a certain metric and returns a list of strings."
    with xr.open_dataset(filepath) as ds:
        variables = _get_metric_var(ds,metric)
    return variables

def _get_metric_var(ds, metric):
    "Searches the dataset for variables that contain a certain metric and returns a list of strings."
    if metric == 'n_obs': #n_obs is a special case, that does not match the usual pattern with *_between*
        return [metric]
    else:
        return [var for var in ds.data_vars if re.search(r'^{}_between'.format(metric), var, re.I)]


def load_data(filepath, variables, extent=None, index_names=globals.index_names):
    """
    converts xarray.DataSet to pandas.DataFrame, reading only relevant variables and multiindex
    """
    with xr.open_dataset(filepath) as ds:
        df = _load_data(ds, variables, extent, index_names)
    return df

def _load_data(ds, variables, extent, index_names):
    """
    converts xarray.DataSet to pandas.DataFrame, reading only relevant variables and multiindex
    """
    if type(variables) is str: variables = [variables] #convert to list of string
    try:
        df = ds[index_names + variables].to_dataframe()
    except KeyError as e:
        raise Exception('The given variabes '+ ', '.join(variables) + ' do not match the names in the input data.' + str(e))
    df.dropna(axis='index',subset=variables, inplace=True)
    if extent: # === geographical subset ===
        lat,lon = globals.index_names
        df=df[ (df.lon>=extent[0]) & (df.lon<=extent[1]) & (df.lat>=extent[2]) & (df.lat<=extent[3]) ]
    return df

def get_meta(filepath,var):
    """
    parses the var name and gets metadata from tha *.nc dataset.
    checks consistency between the dataset and the variable name.
    """
    with xr.open_dataset(filepath) as ds:
        return _get_meta(var,ds)

def _get_meta(var,ds):
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
        pattern = re.compile(r"""(\D+)_between_(\d+)-(\S+)_(\d+)-(?P<dataset>\S+)""") #'ubRMSD_between_4-ISMN_3-ESA_CCI_SM_combined'
        match = pattern.match(var)
        meta['metric'] = match.group(1)
        meta['ref_no'] = int(match.group(2))
        meta['ref'] = match.group(3)
        meta['ds_no'] = int(match.group(4))
        meta['ds'] = match.group(5)
    except AttributeError:
        if var == 'n_obs': #catch error occuring when var is 'n_obs'
            meta['metric'] = 'n_obs'
            meta['ref_no'] = 4 #TODO: find a way to not hard-code this!
            meta['ref'] = 'GLDAS'
            meta['ds_no'] = 1
            meta['ds'] = 'GLDAS'
        else:
            raise Exception('The given var \'{}\' does not match the regex pattern.'.format(var))
    # === read ds metadata
    try:
        meta['ref_pretty_name'] = meta['ref'] #TODO: get pretty name from somewhere!
        meta['ref_version'] = ds.attrs['val_dc_version' + str(meta['ref_no']-1)]
        meta['ref_version_pretty_name'] = meta['ref_version'] #TODO: get versio pretty from somewhere!
        meta['ds_pretty_name'] = meta['ds'] #TODO: get pretty name from somewhere!
        meta['ds_version'] = ds.attrs['val_dc_version' + str(meta['ds_no']-1)]
        meta['ds_version_pretty_name'] = meta['ds_version'] #TODO: get version pretty from somewhere!
    except KeyError as e:
        raise Exception('There is a problem with the dataset attributes:\n' + str(e))
    return meta

def get_varmeta(filepath, variables):
    """
    get meta for all variables and return a nested dict.
    """
    with xr.open_dataset(filepath) as ds:
        return _get_varmeta(variables,ds)

def _get_varmeta(variables,ds):
    """
    get meta for all variables and return a nested dict.
    """
    return {var:_get_meta(var,ds) for var in variables}

def get_globmeta(filepath, variables):
    """
    get globmeta from varmeta and make sure it is consistent in itself.
    """
    varmeta = get_varmeta(filepath,variables)
    return _get_globmeta(varmeta)


def _get_globmeta(varmeta):
    """
    get globmeta from varmeta and make sure it is consistent in itself.
    """
    globkeys = ['metric', 'ref', 'ref_pretty_name', 'ref_version', 'ref_version_pretty_name']
    def get_globdict(meta):
        return {k:meta[k] for k in globkeys}
    variter = iter(varmeta)
    globmeta = get_globdict(varmeta[next(variter)])
    while True: #for loop with iterator: compare if globmeta is universal among all variables
        try:
            var = next(variter)
            if globmeta != get_globdict(varmeta[var]):
                raise Exception('Global Metadata inconsistent among variables!\nglobmeta : {}\nvs.\nglobmeta(\'{}\') : {}'.format(
                        globmeta, var, get_globdict(varmeta[var]) ) )
        except StopIteration:
            break
    return globmeta