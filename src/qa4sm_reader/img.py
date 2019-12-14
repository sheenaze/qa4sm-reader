# -*- coding: utf-8 -*-

import xarray as xr
from qa4sm_reader import globals
from parse import *
import os
import numpy as np
from collections import OrderedDict
from src.qa4sm_reader.handlers import _build_fname_templ
from src.qa4sm_reader.handlers import QA4SMMetricVariable
import pandas as pd

class QA4SMImg(object):
    """
    A QA4SM validation results netcdf image.
    """

    def __init__(self, filepath, extent=None, ignore_empty=True,
                 index_names=globals.index_names):
        """
        Initialise a common QA4SM results image.

        Parameters
        ----------
        filepath : str
            Path to the results netcdf file (as created by QA4SM)
        extent : tuple, optional (default: None)
            Area to subset the data for.
            (min_lon, max_lon, min_lat, max_lat)
        ignore_empty : bool, optional (default: True)
            Ignore empty variables in the file.
        index_names : list, optional (default: ['lat', 'lon'] - as in globals.py)
            Names of dimension variables in x and y direction (lat, lon).
        """
        self.filepath = filepath
        self.filename = os.path.basename(self.filepath)

        self.extent = extent
        self.index_names = index_names

        self.ignore_empty = ignore_empty
        self.ds = xr.load_dataset(self.filepath)

        self.common, self.double, self.triple = self._load_all_metrics_from_file()

    def _load_all_metrics_from_file(self) -> (dict, dict, dict):
        """ Load and group all metrics from file """
        common, double, triple = dict(), dict(), dict()
        for n, metrics in globals.metric_groups.items():
            for metric in metrics:
                metr_vars = self._load_metric_from_file(metric)
                if len(metr_vars) > 0:
                    if metric in globals.metric_groups[2]:
                        double[metric] = metr_vars
                    elif metric in globals.metric_groups[3]:
                        triple[metric] = metr_vars
                    else:
                        common[metric] = metr_vars

        return common, double, triple

    def _load_metric_from_file(self, metric:str) -> np.array:
        """ Load all variables that describe the metric from file. """
        all_vars = np.sort(np.array(list(self.ds.variables.keys())))
        metr_vars = []
        for var in all_vars:
            Var = self._load_var(var)
            if Var is not None and (Var.metric == metric):
                if self.ignore_empty:
                    if not Var.isempty():
                        metr_vars.append(Var)
                else:
                    metr_vars.append(Var)

        return np.array(metr_vars)

    def _load_var(self, varname:str) -> (QA4SMMetricVariable or None):
        """ Create a common variable and fill it with data """
        try:
            vardata = self._ds2df([varname])
            Var = QA4SMMetricVariable(varname, vardata, self.ds.attrs)
            return Var
        except IOError:
            return None

    def _ds2df(self, varnames:list) -> pd.DataFrame:
        """ Cut a variable to extent and return it as a data frame """
        try:
            df = self.ds[self.index_names + varnames].to_dataframe()
        except KeyError as e:
            raise Exception(
                'The given variable ' + ', '.join(varnames) +
                ' do not match the names in the input data.' + str(e))
        df.dropna(axis='index', subset=varnames, inplace=True)
        if self.extent:  # === geographical subset ===
            lat, lon = globals.index_names
            df = df[(df[lon] >= self.extent[0]) & (df[lon] <= self.extent[1]) &
                    (df[lat] >= self.extent[2]) & (df[lat] <= self.extent[3])]
        df.reset_index(drop=True, inplace=True)
        df = df.set_index(self.index_names)
        return df

    def metric_df(self, metric):
        """
        Group all variables for the metric in a common data frame

        Parameters
        ---------
        metric : str
            The name of a metric in the file, all variables for that metric are
            combined into one data frame.

        Returns
        -------
        df : pd.DataFrame
            A dataframe that contains all variables that describe the metric
            in the column
        """
        for metric_group in [self.common, self.double, self.triple]:
            if metric in metric_group.keys():
                conc = [Var.data for Var in metric_group[metric]]
                return pd.concat(conc, axis=1)

    def find_group(self, src):
        """
        Search the element and get the variable group that it is in.

        Parameters
        ---------
        src : str
            Either a metric or a variable

        Returns
        -------
        metric_group : dict
            A collection of metrics for 2, 3 or all datasets.
        """
        for metric_group in [self.common, self.double, self.triple]:
            if src in metric_group.keys():
                return metric_group
        for metric_group in [self.common, self.double, self.triple]:
            for metric in metric_group.keys():
                if src in [Var.name for Var in metric_group[metric]]:
                    return metric_group

    def metric_meta(self, metric):
        """
        Get the meta data for all variables that describe the passed metric.

        Parameters
        ----------
        metric : str
            A metric that is in the file (e.g. n_obs, R, ...)

        Returns
        -------
        metric_meta : dict
            Dictionary of metadata dictionaries, with variables as the keys.
        """

        group = self.find_group(metric)
        metvar_meta = {}
        for Var in group[metric]:
            metvar_meta[Var.name] = Var.get_varmeta()
        return metvar_meta

    def parse_filename(self):
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
        filename = os.path.basename(self.filepath)
        parts = filename.split(globals.ds_fn_sep)
        fname_templ = _build_fname_templ(len(parts))
        return parse(fname_templ, filename).named

    def ls_metrics(self, as_groups=True):
        """
        Get a list of validation METRICS names that are in the current loaded.

        Parameters
        ----------
        as_groups : bool, optional (default: True)
            Return the metrics grouped by whether all datasets, two, or three
            are considered during calculation. If this is False, then all metrics
            are combined in a common list

        Returns
        -------
        metrics : list or OrderedDict
            The (grouped) metrics in the current file.
        """

        single = [m for m in self.common.keys()]
        double = [m for m in self.double.keys()]
        triple = [m for m in self.triple.keys()]

        if as_groups:
            return OrderedDict([('common', single), ('double', double),
                                ('triple', triple)])
        else:
            return sorted(single + double + triple)

    def ls_vars(self):
        """
        Get a list of VARIABLES (except gpi, lon, lat) of the current file.

        Parameters
        ---------
        only_metrics_vars : bool
            Only include variables that describe a validation metric
        exclude_empty : bool, optional (default: True)
            Ignore variables that are empty / all nans from reading

        Returns
        --------
        vars : np.array
            Alphabetically sorted variables in the file (except gpi, lon, lat),
            optionally without the empty variables.
        """
        varnames = []
        for metric_group in [self.common, self.double, self.triple]:
            for metric in metric_group.keys():
                for Var in metric_group[metric]:
                    varnames.append(Var.name)
        return sorted(varnames)

if __name__ == '__main__':
    path = r'H:\code\qa4sm-reader\tests\test_data\basic\3-ERA5_LAND.swvl1_with_1-C3S.sm_with_2-SMOS.Soil_Moisture.nc'
    # 6-ISMN.soil moisture_with_1-C3S.sm_with_2-C3S.sm_with_3-SMOS.Soil_Moisture_with_4-SMAP.soil_moisture_with_5-ASCAT.sm.nc'
    img = QA4SMImg(path)
    vars = img.ls_vars()
    metrics = img.ls_metrics(as_groups=True)
    img.metric_meta('BIAS')
    

"""
class QA4SMDataAttributes(object):
    def __init__(self, short_name, pretty_name, short_version, pretty_version,
                 varnum):
        self.name = name
        self.version = version
        self.varnum = varnum

    def add_meta(self, short_name, pretty_name, pretty_version):
        if short_name != self.name:
            raise ValueError()
        self.meta = {'short_name' : short_name,
                     'pretty_name' : pretty_name,
                     'pretty_version' : pretty_version}


    def is_scattered(self):
        if self.name in globals.scattered_datasets:
            return True

    def pretty_name(self):
        NotImplementedError

if __name__ == '__main__':
    ds = xr.open_dataset(
        r"H:\code\qa4sm-reader\tests\test_data\6-ISMN.soil moisture_with_1-C3S.sm_with_2-C3S.sm_with_3-SMOS.Soil_Moisture_with_4-SMAP.soil_moisture_with_5-ASCAT.sm.nc")
    meta = QA4SMAttributes(global_attrs=ds.attrs)
"""
