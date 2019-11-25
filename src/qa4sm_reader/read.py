# -*- coding: utf-8 -*-
import re

import xarray as xr

from qa4sm_reader import globals
from qa4sm_reader.ncplot import _get_pretty_name
from parse import *
import os

def build_fname_templ(n):
    parts =[globals.fn_templ.format(ds='{ref}', var='{ref_var}')]
    for i in range(1, n):
        parts += [globals.fn_templ.format(ds='{ds%i}'%i, var='{var%i}'%i)]
    return globals.fn_sep.join(parts) + '.nc'

def parse_filename(filename):
    parts = filename.split(globals.fn_sep)
    fname_templ = build_fname_templ(len(parts))
    return parse(fname_templ, filename).named

def parse_varname(varname, form='basic'):
    pass

class QA4SMImg(object):
    """
    Represents a singe QA4SM result (the netcdf file that is created)
    """
    ds = None
    data = None
    meta = None

    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(self.filepath)

    def _load_var_data(self):
        """"
        Searches the dataset for variables that contain a '<metric>_between'
        and returns a list of strings.
        Drop vars that contain only nan or null values.

        Parameters
        ---------
        metric : str or None
            The metric to load
        """
        # TODO: change to set instead of list
        if metric == 'n_obs':  # n_obs is a special case, that does not match the usual pattern with *_between*
            return [metric]
        else:
            vars = [var for var in self.ds if ~self.ds[var].isnull().all()]  # reject all nan and null values.
            if metric:  # usual case.
                return [var for var in vars if
                        re.search(r'^{}_between'.format(metric), var, re.I)]  # search for pattern.
            else:  # metric is None, return all variables that contain '_between'
                return [var for var in vars if
                        (re.search(r'_between', var, re.I) or var == 'n_obs')]  # search for pattern.

    def _get_varmeta(self, ds, variables=None):
        """
        get meta for all variables and return a nested dict.
        """
        if not variables:  # get all variables.
            variables = self._get_var(ds, metric=None)
        return {var: self._get_meta(ds, var) for var in variables}

    def _get_meta(self, ds, var):
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

    def ds2df(self, variables, extent, index_names):
        """
        converts xarray.DataSet to pandas.DataFrame, reading only relevant
        variables and multiindex
        """
        if type(variables) is str: variables = [variables]  # convert to list of string
        try:
            df = self.ds[index_names + variables].to_dataframe()
        except KeyError as e:
            raise Exception(
                'The given variabes ' + ', '.join(variables) + ' do not match the names in the input data.' + str(e))
        df.dropna(axis='index', subset=variables, inplace=True)
        if extent:  # === geographical subset ===
            lat, lon = globals.index_names
            df = df[(df[lon] >= extent[0]) & (df[lon] <= extent[1]) & (df[lat] >= extent[2]) & (df[lat] <= extent[3])]
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
        varmeta : dict
            Dictionary containing a meta dict for each variable in df.
        """
        self.ds = xr.open_dataset(self.filepath)

        if isinstance(metric, str):
            variables = self._get_var(metric)
        elif isinstance(metric, list) or isinstance(metric, set):  # metric is a list and already contais the variables to be plotted.
            variables = metric
        else:
            raise TypeError('The argument metric must be str or list. {} was given.'.format(type(metric)))
        varmeta = self._get_varmeta(self.ds, variables)
        df = self.ds2df(self.ds, variables, extent, index_names)

        self.data = df
        self.meta = varmeta

    def _file_meta(self):
        parse_filename(self.filename)

if __name__ == '__main__':
    afile = "/home/wolfgang/code/qa4sm-reader/tests/test_data/3-GLDAS.SoilMoi0_10cm_inst_with_1-C3S.sm_with_2-ESA_CCI_SM_combined.sm.nc"
    reader = QA4SMImg(afile)
    img = reader.load_metric('R')



# def load_data(filepath, variables, extent=None, index_names=globals.index_names):
#     """
#     Loads requested Data from the NetCDF file.
#
#     Parameters
#     ----------
#     filepath : str
#     variables
#     extent : list
#         [lon_min,lon_max,lat_min,lat_max] to create a subset of the data
#     index_names : list [optional]
#         defaults to globals.index_names = ['lat', 'lon']
#
#     Returns
#     -------
#     df : pandas.DataFrame
#         DataFrame containing the requested data.
#     """
#     with xr.open_dataset(filepath) as ds:
#         df = _load_data(ds, variables, extent, index_names)
#     return df




