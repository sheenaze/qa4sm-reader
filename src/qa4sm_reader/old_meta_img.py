# -*- coding: utf-8 -*-

import re
from pprint import pprint
from parse import parse
from qa4sm_reader import globals
from qa4sm_reader.img import QA4SMImg, parse_filename
import warnings
import numpy as np

class QA4SM_MetaImg(QA4SMImg):
    """
    QA4SM Results with metadata information
    """
    def __init__(self, filepath, extent=None, index_names=globals.index_names):
        super(QA4SM_MetaImg, self).__init__(filepath, extent, index_names)
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
        y = lambda v: self._var2met(v)
        print([y(v) for v in list(self.ds.variables.keys()) if y(v) is not None])
        print('================================================================')
        print('Variables from metrics:\n')
        m_file = self.metrics_in_file()
        metrics = []
        for g, m in m_file.items():
            for i in m: metrics.append(i)
        print([self._met2vars(m) for m in metrics])
        print('================================================================')
        # print the datasets in the file

    def _num2short(self, num=0):
        attr = globals._ds_short_name_attr.format(num)
        if attr not in self.global_meta:
            raise ValueError(num, 'No dataset for that index.')
        return self.global_meta[attr]

    def _short2num(self, short):
        """
        Get the number for a dataset based on the short name. If there are
        duplicate short names in the file, a list is returned.

        Parameters
        ----------
        short : str
            Short name, as in the variable name for example

        Returns
        -------
        num : list or int
            The according identifier(s)
        """
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
        ds_short_names : np.array
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

        return ref_short_name, np.array(ds_short_names)

    def short_to_pretty(self, src, ignore_error=False):
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
        versions : list
            The short version of the dataset, multiple entries if multiple versions
            of the same dataset were used.
        version_pretty_names: list
            The short version of the dataset, multiple entries if multiple versions
            of the same dataset were used.
        """
        if isinstance(src, str):
            short_name = src
            try:
                number = self._short2num(short_name)
            except ValueError as e:
                if ignore_error:
                    number = 9999
                else:
                    raise e
            if isinstance(number, int):
                number = [number]
        elif isinstance(src, int):
            short_name = self._num2short(src)
            number = [src]
        else:
            raise IOError(src, 'Unexpected input format (pass str or int)')

        try:
            pretty_name = [self.ds.attrs[globals._ds_pretty_name_attr.format(n)] for n in number]
            assert all([e==pretty_name[0] for e in pretty_name])
            pretty_name = pretty_name[0]
        except KeyError:
            warnings.warn('Pretty Name not found in file, fallback to globals.')
            try:
                pretty_name = globals._dataset_pretty_names[short_name]
            except KeyError:
                warnings.warn('Pretty Name not found in file and in globals, use version short name.')
                pretty_name = short_name

        versions = []
        versions_pretty_names = []
        for n in number:
            try:
                version = self.ds.attrs[globals._version_short_name_attr.format(n)]
            except KeyError as e:
                raise e
            versions.append(version)
            try:
                version_pretty_name = self.ds.attrs[globals._version_pretty_name_attr.format(n)]
            except KeyError:
                warnings.warn('Version Pretty Name not found in file, fallback to globals.')
                try:
                    version_pretty_name = globals._dataset_version_pretty_names[version]
                except KeyError:
                    warnings.warn('Version Pretty Name not found in file and not in globals, use version name.')
                    version_pretty_name = version
            versions_pretty_names.append(version_pretty_name)

        return pretty_name, versions, versions_pretty_names

    def get_var_meta(self, vars=None):
        """
        get meta for all variables and return a nested dict.

        Parameters
        ---------
        vars : list
            List of variables

        Returns
        --------
        meta : dict
            Meta data for the variable
        n_ds : int
            Number of non reference datasets for the variable
        """
        if not vars:  # get all variables.
            vars = self.vars_in_file()
        return {var: self._var_meta(var) for var in vars}

    def _compile_var(self, var, var_group):
        """Use regex to parse the variable name"""
        meta = dict()
        if var_group == 2:  # basic metrics
            template = r"""(\D+)_between_(\d+)-(\S+)_and_(\d+)-(\S+)"""
            pattern = re.compile(template)
            match = pattern.match(var)
            # metric
            meta['metric'] = match.group(1)
            # datasets
            meta['ref_no'] = int(match.group(2))
            meta['ref'] = match.group(3)
            meta['ds1_no'] = int(match.group(4))
            meta['ds1'] = match.group(5)
            # other
            meta['var_group'] = var_group
            n_ds = 1
        elif var_group == 3:  # TC metrics
            template = r"""(\D+)_(\d+)-(\S+)_between_(\d+)-(\S+)_and_(\d+)-(\S+)_and_(\d+)-(\S+)"""
            pattern =  re.compile(template)
            match = pattern.match(var)
            # metric
            meta['metric'] = match.group(1)
            meta['ds_metric_no'] = int(match.group(2))
            meta['ds_metric'] = match.group(3)
            # reference
            meta['ref_no'] = int(match.group(4))
            meta['ref'] = match.group(5)
            # datasets
            meta['ds1_no'] = int(match.group(6))
            meta['ds1'] = match.group(7)
            meta['ds2_no'] = int(match.group(8))
            meta['ds2'] = match.group(9)
            # other
            meta['var_group'] = var_group
            n_ds = 2
        elif var_group == 0:  # common metrics
            template = r"""(\D+)"""
            pattern = re.compile(template)
            match = pattern.match(var)
            meta['metric'] = match.group(1)
            # we cannot use the variable name in that case, so use the metadata
            ref_short_name, ds_short_names = self.get_short_names()
            meta['ref'] = ref_short_name
            meta['ref_no'] = self._short2num(ref_short_name)
            n_ds = 1
            for ds in np.unique(ds_short_names):
                num = self._short2num(ds)
                if not isinstance(num, list):
                    num = [num]
                for j, n in enumerate(num):
                    meta['ds{}_no'.format(n_ds)] = n
                    meta['ds{}'.format(n_ds)] = ds
                    n_ds += 1
            n_ds -= 1
        else:
            raise ValueError(var_group, 'var_group {} is not supported'.format(var_group))

        return meta, n_ds

    def _var_meta(self, var):
        """
        parses the var name and gets metadata from tha *.nc dataset.
        checks consistency between the dataset and the variable name.
        """
        # === consistency with dataset ===
        if not var in self.ds.variables:
            raise ValueError('The given var \'{}\' is not contained in the dataset.'.format(var))

        metr = self._var2met(var)
        g = self._metr_grp(metr)
        m, n_ds = self._compile_var(var, var_group=g)
        meta = m.copy()

        ref_dss = ['ref'] + ['ds{}'.format(i) for i in range(1, n_ds+1)]
        for ds in ref_dss:  # ref is 0, ds1 is 1 etc
            name = meta[ds]
            number = meta[ds + '_no']
            pretty_name, version, version_pretty_name = \
                self.short_to_pretty(name)
            for v, vpn in zip(version, version_pretty_name):
                meta['{}_pretty_name'.format(ds)] = pretty_name
                meta['{}_version'.format(ds)] = v
                meta['{}_version_pretty_name'.format(ds)] = vpn
            
        return meta

    def load_metric_and_meta(self, metric):
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
        df, vars = self.load_metric(metric)
        varmeta = self.get_var_meta(vars)
        return df, varmeta

def testcase_normal():
    afile=r"H:\code\qa4sm-reader\tests\test_data\3-ERA5_LAND.swvl1_with_1-C3S.sm_with_2-SMOS.Soil_Moisture.nc"

    reader = QA4SM_MetaImg(afile)
    reader.print_info()
    metrics_in_file = reader.metrics_in_file()
    vars_in_file = reader.vars_in_file()
    vars_snr = reader._met2vars('snr')
    vars_R = reader._met2vars('R')

    df_R = reader._ds2df(reader._met2vars('R'))
    meta_nobs = reader._var_meta('n_obs')
    meta_RMSD = reader._var_meta('RMSD_between_3-ERA5_LAND_and_2-SMOS')
    meta_R = reader._var_meta('R_between_3-ERA5_LAND_and_2-SMOS')
    also_df_R, also_meta_R = reader.load_metric_and_meta('R')

    num = reader._short2num('ERA5_LAND') # short name to index number
    pre, v1, pre_vers = reader.short_to_pretty(2) # short name to pretty name
    tty, v2, tty_vers = reader.short_to_pretty('ERA5_LAND')
    assert pre == tty
    assert pre_vers == tty_vers


def testcase_snr():
    afile=r"H:\code\qa4sm-reader\tests\test_data\3-ERA5.swvl1_with_1-SMOS.Soil_Moisture_with_2-SMOS.Soil_Moisture.nc"

    reader = QA4SM_MetaImg(afile)
    reader.print_info()
    metrics_in_file = reader.metrics_in_file()
    vars_in_file = reader.vars_in_file()
    vars_snr = reader._met2vars('snr')
     # vars_R = reader._met2vars('R')

    # df_R = reader._ds2df(reader._met2vars('R'))
    # meta_nobs = reader._var_meta('n_obs')
    # meta_RMSD = reader._var_meta('RMSD_between_3-ERA5_and_2-SMOS')
    # meta_R = reader._var_meta('R_between_3-ERA5_and_2-SMOS')
    # also_df_R, also_meta_R = reader.load_metric_and_meta('R')

    df_snr =  reader._ds2df(reader._met2vars('snr'))

    num = reader._short2num('ERA5') # short name to index number
    pre0, v0, pre_vers0 = reader.short_to_pretty(0) # short name to pretty name
    pre1, v1, pre_vers1 = reader.short_to_pretty(1) # short name to pretty name
    assert (pre0 == pre1) and (v0==v1) and (pre_vers0==pre_vers1)
    pre2, v2, pre_vers2 = reader.short_to_pretty(2) # short name to pretty name
    tty, v2, tty_vers = reader.short_to_pretty('ERA5')
    assert pre2 == tty
    assert pre_vers2 == tty_vers

    df, varmeta = reader.load_metric_and_meta('snr')


if __name__ == '__main__':
    testcase_normal()

    #
    # varsinfile= reader.vars_in_file(exclude_empty=True)
    #
    # short_names = reader.get_short_names() # all short names
    # for var in vars_R + vars_snr:
    #     metric = reader._var2met(var)
    #     meta = reader.get_var_meta([var])
    #
    # reader.print_info()
    #
    # img, vars = reader.load_metric('R')
    # df, varmeta = reader.load_metric_and_meta('R')













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

