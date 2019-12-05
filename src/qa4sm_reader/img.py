# -*- coding: utf-8 -*-

import xarray as xr

from qa4sm_reader import globals
from parse import *
import os


def _build_fname_templ(n):
    """
    Create a template to parse for the file name, based on the dataset-version
    separation rule from globals.

    Parameters
    ----------
    n : int
        Total number of (reference and candidate) data sets in the file.

    Returns
    -------
    fname_templ : str
        Template for the file name to parse.
    """
    parts =[globals.ds_fn_templ.format(i='{i_ref}', ds='{ref}', var='{ref_var}')]
    for i in range(1, n):
        parts += [globals.ds_fn_templ.format(i='{i_ds%i}' % i, ds='{ds%i}' % i, var='{var%i}' % i)]
    return globals.ds_fn_sep.join(parts) + '.nc'

def parse_filename(filename):
    """
    Parse filename and derive the validation datasets. Relies on the separator
    between data sets in the filename from the globals.

    Parameters
    ----------
    filename : str
        File name (not path) to parse based on the rule from globals.

    Returns
    -------
    ds_and_vers : list
        The parsed datasets and version from the file name.
    """
    parts = filename.split(globals.ds_fn_sep)
    fname_templ = _build_fname_templ(len(parts))
    return parse(fname_templ, filename).named

class QA4SM_Img(object):
    """
    A singe QA4SM validation results netcdf file
    """
    def __init__(self, filepath):
        """
        Initialise a single QA4SM results image.

        Parameters
        ----------
        filepath : str
            Path to the results netcdf file (as created by QA4SM)
        vars : list, optional (default: None)
            List of variables in the file to load, if None are passed, all are
            loaded.
        """
        self.filepath = filepath
        self.filename = os.path.basename(self.filepath)
        self.ds = xr.open_dataset(self.filepath)
        self.parameters = list(self.ds.variables.keys())

    def metrics_in_file(self, group=True):
        common, dual, triple, other = [], [], [], []

        for n, metrics in globals.metric_groups.items():
            for metric in metrics:
                vars = self._vars4metric(metric)
                if metric in globals.metric_groups[0] and len(vars) > 0:
                    common.append(metric)
                elif metric in globals.metric_groups[2] and len(vars) > 0:
                    dual.append(metric)
                elif metric in globals.metric_groups[3] and len(vars) > 0:
                    triple.append(metric)
                elif len(vars) > 0:
                    other.append(metric)
        if group:
            return {'common': common, 'dual': dual, 'triple': triple, 'other': other}
        else:
            return common + dual + triple + other

    def _var2metric(self, var):
        """
        Parameters
        ----------
        var : str
            Variable as in the file

        Returns
        -------
        parts : list
            Parsed variable parts

        """
        if var in globals.metric_groups[0]:
            return var

        sep = globals.var_name_metric_sep[2].format(metric='')
        metr = var.split(sep)[0]
        g = self._metr_grp(metr)
        if g is not None:
            return metr
        else:
            parts = parse(metr, var)
            return parts['metric']

    def _ds2df(self, variables, extent=None, index_names=globals.index_names):
        """
        converts xarray.DataSet to pandas.DataFrame, reading only relevant
        variables and multiindex

        Parameters
        ---------
        variables : list or str
            Variables in the file that are included in the data frame.
        extent : tuple, optional (default: None)
            Area to subset the data for.
            (min_lon, max_lon, min_lat, max_lat)
        index_names : list
            Names of the dimensions (x, y) the data is stored in.
        """
        if type(variables) is str: variables = [variables]  # convert to list of string
        try:
            df = self.ds[index_names + variables].to_dataframe()
        except KeyError as e:
            raise Exception(
                'The given variabes ' + ', '.join(variables) +
                ' do not match the names in the input data.' + str(e))
        df.dropna(axis='index', subset=variables, inplace=True)
        if extent:  # === geographical subset ===
            lat, lon = globals.index_names
            df = df[(df[lon] >= extent[0]) & (df[lon] <= extent[1]) &
                    (df[lat] >= extent[2]) & (df[lat] <= extent[3])]
        df.reset_index(drop=True, inplace=True)
        return df

    def load_metric(self, metric, extent=None, index_names=globals.index_names):
        """
        Loads data from *.nc file in filepath and returns it as pandas.DataFrame,
        including a metadata dictionary.

        Parameters
        ----------
        metric : list or str or None
            metric(s) to load
        extent : list, optional
            [lon_min,lon_max,lat_min,lat_max] to create a subset of the data
        index_names : list, optional

        Returns
        -------
        df : pandas.DataFrame
            DataFrame containing the requested data, stripped by nan values and
            cropped to extent.
        vars : list
            Variables for the passed metric
        """

        if isinstance(metric, str):
            vars = self._vars4metric(metric)
        elif isinstance(metric, list) or isinstance(metric, set):  # metric is a list and already contais the variables to be plotted.
            vars = metric
        else:
            raise TypeError('The argument metric must be str or list. '
                            '{} was given.'.format(type(metric)))

        df = self._ds2df(vars, extent, index_names)

        return df, vars

    def _metr_grp(self, metric):
        g = None
        for g in globals.metric_groups.keys():
            if metric in globals.metric_groups[g]:
                break
        return g

    def _vars4metric(self, metric):
        """"
        Searches the dataset for variables that contain a '<metric>_between'
        and returns a list of strings.
        Drop vars that contain only nan or null values.

        Parameters
        ---------
        metric : str, optional (default: None)
            The metric to load (as in global.metric_groups),
            if None is passed, all metric variables are loaded
        """
        g = self._metr_grp(metric)
        vars = [var for var in self.ds if ~self.ds[var].isnull().all()]  # reject all nan and null values.
        ret = []
        for var in vars:
            if g in [2, 3]:
                pattern = '{}{}'.format(globals.var_name_metric_sep[g], globals.var_name_ds_sep[g])
            else: # not metrics
                pattern = globals.var_name_metric_sep[g]
            parts = parse(pattern, var)
            if parts is not None and 'metric' in parts and parts['metric'] == metric:
                ret.append(var)
        return ret
