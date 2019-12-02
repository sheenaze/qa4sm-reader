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

from qa4sm_reader import globals
import xarray as xr


#from qa4sm_reader.read import load, _vars4metric, meta_get_varmeta, _get_meta


# === File level ===

def get_metrics(filepath):
    "Returns a list of metrics available in the current filepath"
    with xr.open_dataset(filepath) as ds:
        metrics = _get_metrics(ds)
    return metrics

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

def get_varmeta(filepath, variables=None):
    """
    get meta for all variables and return a nested dict.
    """
    with xr.open_dataset(filepath) as ds:
        return _get_varmeta(ds, variables)



