# -*- coding: utf-8 -*-

from qa4sm_reader import globals
from parse import *
import warnings

def _build_fname_templ(n):
    """
    Create a template to parse for the file name, based on the dataset-__version
    separation rule from globals.

    Parameters
    ----------
    n : int
        Total number of (reference and candidate) values sets in the file.

    Returns
    -------
    fname_templ : str
        Template for the file name to parse.
    """
    parts =[globals.ds_fn_templ.format(i='{i_ref:d}', ds='{ref}', var='{ref_var}')]
    for i in range(1, n):
        parts += [globals.ds_fn_templ.format(i='{i_ds%i:d}' % i, ds='{ds%i}' % i,
                                             var='{var%i}' % i)]
    return globals.ds_fn_sep.join(parts) + '.nc'

def _metr_grp(metric:str) -> int or None:
    for g in globals.metric_groups.keys():
        if metric in globals.metric_groups[g]:
            return g
    return None

class QA4SMAttributes(object):
    """ Attribute handler for QA4SM results, only from meta values """
    def __init__(self, global_attrs):
        """
        Parameters
        ----------
        global_attrs: dict
            Global attributes of the QA4SM validation result
        """
        self.meta = global_attrs
        self._get_offset()
        self.other_dcs, self.ref_dc = self._dcs()

    def _get_offset(self):
        self._offset_id_dc = 0
        if 'val_ref' in self.meta.keys():
            id = int(parse('val_dc_dataset{id}', self.meta['val_ref'])['id'])
            if id != 0:
                self._offset_id_dc = -1

    def _dcs(self):
        """ Go through the metadata and find the dataset short names """
        ref_dc = self._ref_dc()
        dcs = dict()
        for k in self.meta.keys():
            parsed = parse(globals._ds_short_name_attr, k)
            if parsed is not None and len(list(parsed)) == 1:
                dc = list(parsed)[0]
                if dc != ref_dc:
                    dcs[dc] = k
        return dcs, ref_dc

    def _ref_dc(self):
        """ Get the short name of the reference dataset """
        val_ref = self.meta[globals._ref_ds_attr]
        ref_dc = parse(globals._ds_short_name_attr, val_ref)[0]
        return ref_dc

    def _dc_names(self, dc):
        """
        Get dataset meta values for the passed dc.

        Parameters
        ----------
        dc : int
            The id of the dataset as in the global metadata of the results file

        Returns
        -------
        names : dict
            short name, pretty_name and short_version and pretty_version of the
            dc dataset.
        """
        short_name = self.meta[globals._ds_short_name_attr.format(dc)]
        pretty_name = self.meta[globals._ds_pretty_name_attr.format(dc)]
        short_version = self.meta[globals._version_short_name_attr.format(dc)]
        pretty_version = self.meta[globals._version_pretty_name_attr.format(dc)]

        return dict(short_name=short_name, pretty_name=pretty_name,
                    short_version=short_version, pretty_version=pretty_version)

    def get_all_names(self) -> (dict, dict):
        """
        Get 2 dictionaries of names, one for the ref names, one for the
        satellite ds names.
        """
        return self.get_ref_names(), self.get_other_names()

    def get_other_names(self) -> dict :
        """ Get a dictionary with names of the non-reference values sets"""
        ret = dict()
        for dc in self.other_dcs:
            ret[dc] = self._dc_names(dc)
        return ret

    def get_ref_names(self) -> dict :
        """ Get a dictionary with names of the non-reference values sets"""
        return self._dc_names(self._ref_dc())

class QA4SMNamedAttributes(QA4SMAttributes):
    """ Attribute handler for named QA4SM datasets, based on global attributes."""

    def __init__(self, id, short_name, global_attrs):
        """
        QA4SMNamedAttributes handler for metdata lookup

        Parameters
        ----------
        id : int
            Id of the dataset as in the VARIABLE NAME (not as in the attributes)
        short_name : str
            Short name of the dataset as in the variable name
        global_attrs : dict
            Global attributes of the results file, for lookup.
        """
        super(QA4SMNamedAttributes, self).__init__(global_attrs)

        self.id = id
        self.__short_name = short_name
        self.__version = self._names_from_attrs('short_version')

        try:
            assert self.short_name == self._names_from_attrs('short_name')
        except AssertionError as e:
            raise(e, f"Short name {self.short_name} does not match to the name in "
                     f"attributes {self._names_from_attrs('short_name')}. "
                     f"Is the id correct (as in the variable name)?")
    @property
    def short_name(self) -> str:
        return self.__short_name

    @property
    def version(self) -> str:
        return self.__version

    def __eq__(self, other):
        if (self.version == other.version) and \
            (self.short_name == other.short_name) :
            return  True
        else:
            return False

    def _id2dc(self) -> int:
        return self.id + self._offset_id_dc

    def _names_from_attrs(self, element='all'):
        """
        Get names for this dataset

        Parameters
        ----------
        elements : str or list
            'all' or '__short_name' or 'pretty_name' or 'short_version' or
            'pretty_version'

        Returns
        -------
        dict or str : names
            The names as a dictionary
        """
        if isinstance(element, str):
            element = [element]

        dc = self._id2dc()
        names = self._dc_names(dc=dc)
        if element == ['all']:
            element = list(names.keys())
        else:
            if not all([e in list(names.keys()) for e in element]):
                raise ValueError("Elements must be either 'all' or one or "
                                 "mutliple of {}".format(
                    ', '.join(list(names.keys()))))

        if len(element) == 1:
            return names[element[0]]
        else:
            return {e: names[e] for e in element}

    def pretty_name(self) -> str:
        """ get the pretty name, from meta or from globals.py """
        try:
            return self._names_from_attrs('pretty_name')
        except AttributeError: # todo: what exception
            warnings.warn('pretty name not found in metadata, fallback to globals.py')
            if self.__short_name in globals._dataset_pretty_names.keys():
                return globals._dataset_pretty_names[self.__short_name]
            else:
                warnings.warn('pretty name also not found in globals.py, use short name')
                return self.__short_name

    def pretty_version(self) -> str:
        """ get the pretty __version name, from meta or from globals.py """
        try:
            return self._names_from_attrs('pretty_version')
        except AttributeError:
            warnings.warn('pretty __version not found in metadata, fallback to globals.py')
            if self.__version in globals._dataset_version_pretty_names.keys():
                return globals._dataset_version_pretty_names[self.__version]
            else:
                warnings.warn('pretty __version also not found in globals, use __version')
                return self.__version


class QA4SMMetricVariable(object):

    def __init__(self, varname, global_attrs, values=None):
        """
        Validation results for a validation metric and a combination of datasets.

        Parameters
        ---------
        name : str
            Name of the variable
        global_attrs : dict
            Global attributes of the results.
        values : pd.DataFrame, optional (default: None)
            Values of the variable, to store together with the metadata.
        """

        self.varname = varname
        self.attrs = global_attrs
        self.metric, self.g, parts = self._parse_varname()
        self.ref_ds, self.other_dss, self.metric_ds = self._named_attrs(parts)
        self.values = values

    def _named_attrs(self, parts:dict) -> \
            (QA4SMNamedAttributes, list, QA4SMNamedAttributes):
        """ get the datasets from the current variable"""

        if not self.ismetr():
            raise IOError(self.varname, '{} is not in form of a QA4SM metric variable.')

        if self.g == 0:
            a = QA4SMAttributes(self.attrs)
            ref_ds = QA4SMNamedAttributes(a.ref_dc - a._offset_id_dc,
                                          a.get_ref_names()['short_name'], self.attrs)
            return ref_ds, None, None
        else:
            dss = []
            ref_ds = QA4SMNamedAttributes(parts['ref_id'], parts['ref_ds'], self.attrs)
            ds = QA4SMNamedAttributes(parts['sat_id0'], parts['sat_ds0'], self.attrs)
            dss.append(ds)
            if self.g == 3:
                ds = QA4SMNamedAttributes(parts['sat_id1'], parts['sat_ds1'], self.attrs)
                dss.append(ds)
                mds = QA4SMNamedAttributes(parts['mds_id'], parts['mds'], self.attrs)
            else:
                mds = None
            return ref_ds, dss, mds

    def _parse_varname(self) -> (str, int, dict):
        """ parse the name to get the metric, group and  """

        metr_groups = list(globals.metric_groups.keys())
        for g in metr_groups:
            templ_d = globals.var_name_ds_sep[g]
            pattern = '{}{}'.format(globals.var_name_metric_sep[g],
                                    templ_d if templ_d is not None else '')
            parts = parse(pattern, self.varname)

            if parts is not None and parts['metric'] in globals.metric_groups[g]:
                return parts['metric'], g, parts.named

        return None, None, None

    def ismetr(self) -> bool:
        """ Check whether this is a metric variable or not """

        return True if self.metric is not None else False

    def isempty(self):
        """ Check whether values are associated with the object or not """

        if self.values is None or self.values.empty:
            return True

    def get_varmeta(self):
        """
        Get the dataset names based on metadata information

        Returns
        -------
        ref_meta : tuple or None
            Names for the reference dataset
        dss_meta : list of tuples or NOne
            Names for the satellite datasets
        mds_meta : tuple or None
            Names for the metric dataset (TC only)
        """

        if self.ref_ds is not None:
            ref_meta = (self.ref_ds.id, self.ref_ds._names_from_attrs('all'))
        else:
            ref_meta = None
        if self.other_dss is not None:
            dss_meta = [(ds.id, ds._names_from_attrs('all')) for ds in self.other_dss]
        else:
            dss_meta = None
        if self.metric_ds is not None:
            mds_meta = (self.metric_ds.id, self.metric_ds._names_from_attrs('all'))
        else:
            mds_meta = None

        return ref_meta, dss_meta, mds_meta