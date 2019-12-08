# -*- coding: utf-8 -*-

import xarray as xr

from qa4sm_reader import globals
from parse import *
import os
import numpy as np

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


class QA4SMImg(object):
    """
    A singe QA4SM validation results netcdf image file
    """
    def __init__(self, filepath, extent=None, index_names=globals.index_names):
        """
        Initialise a single QA4SM results image.

        Parameters
        ----------
        filepath : str
            Path to the results netcdf file (as created by QA4SM)
        extent : tuple, optional (default: None)
            Area to subset the data for.
            (min_lon, max_lon, min_lat, max_lat)
        index_names : list, optional (default: ['lat', 'lon'] - as in globals.py)
            Names of dimension variables in x and y direction (lat, lon).
        """

        self.filepath = filepath
        self.extent = extent
        self.index_names = index_names
        self.filename = os.path.basename(self.filepath)
        self.ds = xr.open_dataset(self.filepath)
        self.parameters = list(self.ds.variables.keys())

    def _var2met(self, var):
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

    def _met2vars(self, metric):
        g = self._metr_grp(metric)
        vars = [var for var in self.ds if ~self.ds[var].isnull().all()]  # reject all nan and null values.
        ret = []
        for var in vars:
            if g in [2, 3]:
                pattern = '{}{}'.format(globals.var_name_metric_sep[g], globals.var_name_ds_sep[g])
            else:  # not metrics
                pattern = globals.var_name_metric_sep[g]
            parts = parse(pattern, var)
            if parts is not None and 'metric' in parts and parts['metric'] == metric:
                ret.append(var)
        return ret

    def _ds2df(self, variables):
        if isinstance(variables, str): variables = [variables]  # convert to list of string
        try:
            df = self.ds[self.index_names + variables].to_dataframe()
        except KeyError as e:
            raise Exception(
                'The given variabes ' + ', '.join(variables) +
                ' do not match the names in the input data.' + str(e))
        df.dropna(axis='index', subset=variables, inplace=True)
        if self.extent:  # === geographical subset ===
            lat, lon = globals.index_names
            df = df[(df[lon] >= self.extent[0]) & (df[lon] <= self.extent[1]) &
                    (df[lat] >= self.extent[2]) & (df[lat] <= self.extent[3])]
        df.reset_index(drop=True, inplace=True)
        return df

    @staticmethod
    def _metr_grp(metric):
        g = None
        for g in globals.metric_groups.keys():
            if metric in globals.metric_groups[g]:
                break
        return g

    def parse_filename(self):
        """
        Parse the input file name and derive data set names and variables from it.

        Returns
        -------
        ds_and_vers : dict
            The parsed datasets and version from the file name.
        """
        filename = os.path.basename(self.filepath)
        return parse_filename(filename)

    def metrics_in_file(self, group=True):
        """
        Get a list of validation METRICS that are in the current result image.

        Parameters
        ----------
        group : bool, optional (default: True)
            Return the metrics grouped by whether all datasets, two, or three
            are considered during calculation. If this is False, then all metrics
            are combined in a single list

        Returns
        -------
        metrics : list or dict
            The (grouped) metrics in the current file.
        """

        single, double, triple, other = [], [], [], []

        for n, metrics in globals.metric_groups.items():
            for metric in metrics:
                vars = self._met2vars(metric)
                if metric in globals.metric_groups[0] and len(vars) > 0:
                    single.append(metric)
                elif metric in globals.metric_groups[2] and len(vars) > 0:
                    double.append(metric)
                elif metric in globals.metric_groups[3] and len(vars) > 0:
                    triple.append(metric)
                elif len(vars) > 0:
                    other.append(metric)
        if group:
            return {'single': single, 'double': double, 'triple': triple, 'other': other}
        else:
            return single + double + triple + other

    def vars_in_file(self, exclude_empty=True):
        """
        Get a list of VARIABLES (except gpi, lon, lat) of the current file.

        Parameters
        ---------
        exclude_empty : bool, optional (default: True)
            Ignore variables that are empty / all nans from reading

        Returns
        --------
        vars : np.array
            Alphabetically sorted variables in the file (except gpi, lon, lat),
            optionally without the empty variables.
        """
        allvars = np.sort(np.array(list(self.ds.variables.keys())))
        exclude = [ind for ind in globals.index_names] + ['gpi']
        filtered = [var for var in allvars if var not in exclude]

        empty_vars = []
        if exclude_empty:
            for var in filtered:
                if not np.any(np.isfinite(self.ds.variables[var])):
                    empty_vars.append(var)
            return np.array([v for v in filtered if v not in empty_vars])
        else:
            return np.array(filtered)

    def load_metric(self, metric):
        """
        Loads results for a given METRIC the file as a DataFrame.

        Parameters
        ----------
        metric : str
            metric to load

        Returns
        -------
        df : pandas.DataFrame
            DataFrame containing the requested data, stripped by nan values and
            cropped to extent.
        vars : list
            Variables for the passed metric
        """

        if isinstance(metric, str):
            vars = self._met2vars(metric)
        elif isinstance(metric, list) or isinstance(metric, set):  # metric is a list and already contais the variables to be plotted.
            vars = metric
        else:
            raise TypeError('The argument metric must be str or list. '
                            '{} was given.'.format(type(metric)))

        df = self._ds2df(vars)

        return df, vars


if __name__ == '__main__':
    filepath =r"H:\code\qa4sm-reader\tests\test_data\3-ERA5_LAND.swvl1_with_1-C3S.sm_with_2-SMOS.Soil_Moisture.nc"
    img = QA4SMImg(filepath)
    parsed = img.parse_filename()