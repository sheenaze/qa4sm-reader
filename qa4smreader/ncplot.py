# -*- coding: utf-8 -*-
"""
Contains an interface for opening QA4SM output files (*.nc) and producing plots using the dfplot module in this package.
"""
import dfplot
import globals
import xarray as xr
import matplotlib.pyplot as plt
import re
import os

def get_metric_var(filepath, metric):
    with xr.open_dataset(filepath) as ds:
        variables = [var for var in ds.data_vars if re.search(r'^{}(_between|$)'.format(metric), var, re.I)] #TODO: unexpected behaviour. n_obs is matched, altough there is no '_between'. #TODO: n_obs should also be matched (var in df is 'n_obs')
    return variables

def boxplot(filepath, variables, out_dir=None, out_name=None, format=None , **plot_kwargs):
    """
    Creates a boxplot, displaying the variables given as input. 
    Saves a figure and returns Matplotlib fig and ax objects for further processing.
    
    Parameters
    ----------
    filepath : str
        Path to the *.nc file to be processed.
    variables : str of list of str
        Variables to be plotted.
    out_dir : [ None | str ], optional
        Path to output file format. 
        If None, defaults to, the input filepath.
        The default is None.
    out_name : [ None | str ], optional
        Name of output file. 
        If None, defaults to a name that is generated based on the variables.
        The default is None.
    format : [ None | str ], optional
        The file format, e.g. 'png', 'pdf', 'svg', 'tiff'...
        If None, no file is saved.
        The default is png.
    dpi : [ None | scalar > 0 | 'figure' ]
        The resolution in dots per inch. If None, defaults to rcParams["savefig.dpi"]. If 'figure', uses the figure's dpi value.
        The default is None.
    **plot_kwargs : dict, optional
        Additional keyword arguments that are passed to dfplot.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure containing the axes for further processing.
    ax : matplotlib.axes.Axes or list of Axes objects
        Axes or list of axes containing the plot.

    """
    if type(variables) is str: variables = [variables] #convert to list of string

    # === Get ready... ===
    with xr.open_dataset(filepath) as ds:
        # === Get Metadata ===
        varmeta = get_varmeta(variables, ds)
        globmeta = get_globmeta(varmeta)
        # === Load data ===
        df = load_data(ds, variables, globals.index_names)

    # === plot data ===
    fig,ax = dfplot.boxplot(df=df, varmeta = varmeta, globmeta = globmeta, **plot_kwargs)

    # == save figure ===
    if format:
        if not out_dir:
            out_dir = os.path.dirname(__file__)
        if not out_name:
            out_name = 'boxplot_' + '__'.join([var for var in variables])
        filename = os.path.join(out_dir,out_name)
        if type(format) is not list: format = [format] 
        for ending in format:
            plt.savefig('{}.{}'.format(filename, ending), dpi='figure')
    else:
        plt.show()
    #plt.close()
    return fig,ax

def mapplot(filepath, var, out_dir=None, out_name=None, format=None, **plot_kwargs):
    #TODO: do something when var is not a string but a list. (e.g. call list plot function)
    if type(var) == list: var = var[0]
    # === Get ready... ===
    with xr.open_dataset(filepath) as ds:
        # === Get Metadata ===
        meta = get_meta(var, ds)
        # === Load data ===
        df = load_data(ds, var, globals.index_names)

    # === plot data ===
    if ( meta['ds'] in globals.scattered_datasets or meta['ref'] in globals.scattered_datasets ): #do scatterplot
        fig,ax = dfplot.scatterplot(df=df, var = var, meta = meta, **plot_kwargs)
    else:
        fig,ax = dfplot.mapplot(df=df, var = var, meta = meta, **plot_kwargs)

    # == save figure ===
    if format:
        if not out_dir:
            out_dir = os.path.dirname(__file__)
        if not out_name:
            out_name = 'mapplot_' + var
        filename = os.path.join(out_dir,out_name)
        if type(format) is not list: format = [format] 
        for ending in format:
            plt.savefig('{}.{}'.format(filename, ending), dpi='figure')
    else:
        plt.show()
    plt.close()
    #return fig,ax

def load_data(ds,variables,index_names):
    """
    converts xarray.DataSet to pandas.DataFrame, reading only relevant variables and multiindex
    """
    if type(variables) is str: variables = [variables] #convert to list of string
    try:
        df = ds[index_names + variables].to_dataframe()
    except KeyError as e:
        raise Exception('The given variabes '+ ', '.join(variables) + ' do not match the names in the input data.' + str(e))
    return df.dropna(axis='index',subset=variables)

def get_meta(var,ds):
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

def get_varmeta(variables,ds):
    """
    get meta for all variables and return a nested dict.
    """
    return {var:get_meta(var,ds) for var in variables}

def get_globmeta(varmeta):
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

import usecases #for debugging
if __name__ == '__main__':
    usecases.usecase()