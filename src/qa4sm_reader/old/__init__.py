# -*- coding: utf-8 -*-
"""
Created on Dec 04 13:44 2019

@author: wolfgang
"""

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
            i = 1  # numbers as in meta and var. In QA4SMAttributes, it is numbers-1
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
    pattern = re.compile(r"""(\D+)_(\d+)-(\S+)_between_(\d+)-(\S+)_and_(\d+)-(\S+)_and_(\d+)-(\S+)""")
    match = pattern.match(var)
    meta['metric'] = [match.group(1), match.group(2), match.group(3)]
    meta['ref_no'] = int(match.group(4))
    meta['ref'] = match.group(5)
    meta['ds1_no'] = int(match.group(6))
    meta['ds1'] = match.group(7)
    meta['ds2_no'] = int(match.group(8))
    meta['ds2'] = match.group(9)
    meta['g'] = g