# -*- coding: utf-8 -*-
import re

import xarray as xr

from qa4sm_reader import globals
from parse import *
import os
from pprint import pprint

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

    def print_info(self):
        print('File Location:', self.filepath)
        print('================================================================')
        print('Variables:\n')
        print(list(self.ds.variables.keys()))
        print('================================================================')
        print('Names from filename:\n')
        pprint(parse_filename(self.filename))
        print('================================================================')
        print('Metrics in file:\n')
        pprint(self.metrics_in_file())
        print('================================================================')
        # print the current file location
        # print the metrics in the file
        # print the datasets in the file

    def metrics_in_file(self):
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

        return {'common': common, 'dual': dual, 'triple': triple, 'other': other}

    def _var2metric(self, var):
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

class QA4SM_MetaImg(QA4SM_Img):
    """
    QA4SM Results with metadata information
    """
    def __init__(self, filepath):
        super(QA4SM_MetaImg, self).__init__(filepath)
        self.global_meta = self.ds.attrs
        self.var_meta = {var: self.ds.variables[var].attrs for var in self.ds.variables}

    def num2short(self, num=0):
        attr = globals._ds_short_name_attr.format(num)
        if attr not in self.global_meta:
            raise ValueError(num, 'No dataset for that index.')
        return self.global_meta[attr]

    def short2num(self, short):
        glob_meta_inverted = dict()
        for key, value in self.global_meta.items():
            glob_meta_inverted.setdefault(value, list()).append(key)
        #glob_meta_inverted = dict(map(reversed, self.global_meta.items()))
        if short not in glob_meta_inverted:
            raise ValueError(short, 'Short name not found in global attributes')
        ds_short_name_attr = glob_meta_inverted[short]
        # what if not a short name but some other name was passed?
        nums_parse = [parse(globals._ds_short_name_attr, attr) for attr in list(ds_short_name_attr)]
        nums = []
        for num in nums_parse:
            if num is None:
                continue
            try:
                n = int(num[0])
            except ValueError: # e.g. if the pretty name is the same as the short name
                continue
            nums.append(n)
        return nums[0] if len(nums) == 1 else None if len(nums) == 0 else nums

    def get_short_names(self):
        """
        Get all short names in the current results

        Returns
        -------
        ref_short_name : str
            Short name of the reference data set
        ds_short_names : list
            List of short names of the non-reference data sets
        """
        ref_short_name = self.ds.attrs[self.ds.attrs[globals._ref_ds_attr]]
        ds_short_names = []
        for k in self.ds.attrs.keys():
            pattern = r"^{}".format(globals._ds_short_name_attr.format(0).replace("0", "[0-9]+$"))
            if bool(re.match(pattern, str(k))):
                attr = self.ds.attrs[k]
                if attr != ref_short_name:
                    ds_short_names.append(attr)

        return ref_short_name, ds_short_names

    def short_to_pretty(self, src):
        """
        Read the pretty name of a dataset from the metadata.
        First tries to find info from ds.attrs. Then falls back to globals.
        Then falls back to using name as pretty name.

        Parameters
        ---------
        src : int or str
            The dataset ID or the short name as in the file

        Returns
        -------
        pretty_name : str
            The pretty name of the dataset.
        version : str
            The short version of the dataset.
        version_pretty_name.
            The pretty version of the dataset.
        """
        if isinstance(src, str):
            short_name = src
            number = self.short2num(short_name)
            if isinstance(number, int):
                number = [number]
        elif isinstance(src, int):
            short_name = self.num2short(src)
            number = [src]
        else:
            raise IOError(src, 'Unexpected input format (pass str or int)')

        try:
            pretty_name = [self.ds.attrs[globals._ds_pretty_name_attr.format(n)] for n in number]
            assert all([e==pretty_name[0] for e in pretty_name])
            pretty_name = pretty_name[0]
        except KeyError:
            try:
                pretty_name = globals._dataset_pretty_names[short_name]
            except KeyError:
                pretty_name = short_name
        try:
            version = [self.ds.attrs[globals._version_short_name_attr.format(n)] for n in number]
            assert all([e==version[0] for e in version])
            version = version[0]
            try:
                version_pretty_name = [self.ds.attrs[globals._version_pretty_name_attr.format(n)] for n in number]
                assert all([e == version_pretty_name[0] for e in version_pretty_name])
                version_pretty_name = version_pretty_name[0]
            except KeyError:
                try:
                    version_pretty_name = globals._dataset_version_pretty_names[version]
                except KeyError:
                    version_pretty_name = version
        except KeyError:
            version = 'unknown'
            version_pretty_name = 'unknown version'

        return pretty_name, version, version_pretty_name

    def _get_metrics(self):
        varmeta = self.meta_get_varmeta(self)
        return {varmeta[meta]['metric'] for meta in varmeta}

    def meta_get_varmeta(self, vars=None):
        """
        get meta for all variables and return a nested dict.

        Parameters
        ---------
        vars :
        """
        if not vars:  # get all variables.
            vars = self._vars4metric(None)
        return {var: self._get_meta(var) for var in vars}

    def _get_meta(self, var):
        """
        parses the var name and gets metadata from tha *.nc dataset.
        checks consistency between the dataset and the variable name.
        """
        # === consistency with dataset ===
        if not var in self.ds.variables:
            raise ValueError('The given var \'{}\' is not contained in the dataset.'.format(var))
        # === parse var ===
        meta = dict()
        metr = self._var2metric(var)
        if (metr in globals.metric_groups[0]) or (metr in globals.metric_groups[2]):
            try:
                g = 2
                pattern = re.compile(r"""(\D+)_between_(\d+)-(\S+)_and_(\d+)-(\S+)""")
                match = pattern.match(var)
                meta['metric'] = match.group(1)
                meta['ref_no'] = int(match.group(2))
                meta['ref'] = match.group(3)
                meta['ds_no'] = int(match.group(4))
                meta['ds'] = match.group(5)
                meta['g'] = g
            except AttributeError:
                g = 0
                if var == 'n_obs':  # catch error occurring when var is 'n_obs'
                    meta['metric'] = 'n_obs'
                    datasets = {}
                    i = 1  # numbers as in meta and var. In Attributes, it is numbers-1
                    while True:
                        try:
                            datasets[i] = self.ds.attrs['val_dc_dataset' + str(i - 1)]
                            i += 1
                        except KeyError:
                            break
                    try:
                        meta['ref_no'] = int(self.ds.attrs['val_ref'][-1])  # last character of string is reference number
                        meta['ref'] = self.ds.attrs[self.ds.attrs['val_ref']]  # e.g. val_ref = "val_dc_dataset3"
                    except KeyError:  # for some reason, the attribute lookup failed. Fall back to the last element in dict
                        meta['ref_no'] = list(datasets)[-1]
                        meta['ref'] = datasets[meta['ref_no']]
                    datasets.pop(meta['ref_no'])
                    meta['ds_no'] = list(datasets.keys())  # list instead of int
                    meta['ds'] = [datasets[i] for i in meta['ds_no']]  # list instead of str
                    meta['g'] = g
                else:
                    raise Exception('The given var \'{}\' does not match the regex pattern.'.format(var))
        else:  # TC
            g = 3
            pattern =  re.compile(r"""(\D+)_(\d+)-(\S+)_between_(\d+)-(\S+)_and_(\d+)-(\S+)_and_(\d+)-(\S+)""")
            match = pattern.match(var)
            meta['metric'] = [match.group(1), match.group(2), match.group(3)]
            meta['ref_no'] = int(match.group(4))
            meta['ref'] = match.group(5)
            meta['ds1_no'] = int(match.group(6))
            meta['ds1'] = match.group(7)
            meta['ds2_no'] = int(match.group(8))
            meta['ds2'] = match.group(9)
            meta['g'] = g

        dss = ('ds', 'ref') if g in [0,2] else ('ds1', 'ds2', 'ref')
        for i in dss:
            name = meta[i]
            number = meta[i + '_no']
            if (type(name) == list) and (
                    type(number) == list):  # e.g. ds of n_obs are several: the rest needs to be list as well
                meta[i + '_pretty_name'] = list()
                meta[i + '_version'] = list()
                meta[i + '_version_pretty_name'] = list()
                for na, no in zip(name, number):
                    pretty_name, version, version_pretty_name = \
                        self.short_to_pretty(na)
                    meta[i + '_pretty_name'].append(pretty_name)
                    meta[i + '_version'].append(version)
                    meta[i + '_version_pretty_name'].append(version_pretty_name)
            else:  # usual case.
                pretty_name, version, version_pretty_name = \
                    self.short_to_pretty(name)
                meta[i + '_pretty_name'] = pretty_name
                meta[i + '_version'] = version
                meta[i + '_version_pretty_name'] = version_pretty_name

        return meta

    def load_metric_and_meta(self, metric, extent=None, index_names=globals.index_names):
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
        df, vars = self.load_metric(metric, extent, index_names)
        varmeta = self.meta_get_varmeta(vars)
        return df, varmeta

if __name__ == '__main__':
    afile=r"H:\code\qa4sm-reader\tests\test_data\3-ERA5.swvl1_with_1-SMOS.Soil_Moisture_with_2-SMOS.Soil_Moisture.nc"
    reader = QA4SM_MetaImg(afile)
    reader.print_info()
    metrics_in_file = reader.metrics_in_file()
    vars_snr = reader._vars4metric('snr')
    vars_R = reader._vars4metric('R')

    df_R_1 = reader._ds2df(reader._vars4metric('R'), extent=None)
    meta_R = reader._get_meta('R_between_3-ERA5_and_1-SMOS')
    meta_beta = reader._get_meta('beta_2-SMOS_between_3-ERA5_and_1-SMOS_and_2-SMOS')
    df_R, meta_R = reader.load_metric_and_meta('R')

    num = reader.short2num('ERA5') # short name to index number
    pre, v1, pre_vers = reader.short_to_pretty(2) # short name to pretty name
    tty, v2, tty_vers = reader.short_to_pretty('ERA5')
    assert pre == tty
    assert pre_vers == tty_vers

    short_names = reader.get_short_names() # all short names
    for var in vars:
        meta = reader.meta_get_varmeta(var)
    reader.print_info()
    img = reader.load_metric('R')
    #img = reader.load_dataset('ESA_CCI_SM')

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




