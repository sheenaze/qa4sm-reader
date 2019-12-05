# -*- coding: utf-8 -*-
"""
Created on Dec 04 12:19 2019

@author: wolfgang
"""
import re
from pprint import pprint

from parse import parse

from qa4sm_reader import globals
from qa4sm_reader.img import QA4SM_Img, parse_filename


class QA4SM_MetaImg(QA4SM_Img):
    """
    QA4SM Results with metadata information
    """
    def __init__(self, filepath):
        super(QA4SM_MetaImg, self).__init__(filepath)
        self.global_meta = self.ds.attrs
        self.var_meta = {var: self.ds.variables[var].attrs for var in self.ds.variables}

    def print_info(self):
        print('File Location:', self.filepath)
        print('================================================================')
        print('Names from filename:\n')
        pprint(parse_filename(self.filename))
        print('================================================================')
        print('Metrics in file:\n')
        pprint(self.metrics_in_file())
        print('================================================================')
        print('Variables:\n')
        print(list(self.ds.variables.keys()))
        print('================================================================')
        print('================================================================')
        print('Metrics from variables:\n')
        print([self._var2metric(var) for var in self.ds.variables.keys()])
        print('================================================================')
        print('Variables from metrics:\n')
        m_file = self.metrics_in_file()
        metrics = []
        for g, m in m_file.items():
            for i in m: metrics.append(i)
        print([self._vars4metric(m) for m in metrics])
        print('================================================================')
        # print the datasets in the file


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
        vars : list
            List of variables
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
    for var in vars_R + vars_snr:
        metric = reader._var2metric(var)
        meta = reader.meta_get_varmeta([var])

    reader.print_info()

    img, vars = reader.load_metric('R')
    df, varmeta = reader.load_metric_and_meta('R')
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

