# -*- coding: utf-8 -*-


__author__ = "Lukas Racbhauer"
__copyright__ = "2019, TU Wien, Department of Geodesy and Geoinformation"
__license__ = "mit"


"""
Settings and global variables collected from different sources. 
"""


import cartopy.crs as ccrs


# === plot defaults ===
matplotlib_ppi = 72  # Don't change this, it's a matplotlib convention.
index_names = ['lat', 'lon']  # Names used for 'lattitude' and 'longitude' coordinate.
dpi = 100  # Resolution in which plots are going to be rendered.
title_pad = 12.0  # Padding below the title in points. default padding is matplotlib.rcParams['axes.titlepad'] = 6.0
data_crs = ccrs.PlateCarree()  # Default map projection. use one of

# === map plot defaults ===
scattered_datasets = ['ISMN']  # dataset names which require scatterplots (data is scattered in lat/lon)
map_figsize = [11.32, 6.10]  # size of the output figure in inches.
naturalearth_resolution = '110m'  # One of '10m', '50m' and '110m'. Finer resolution slows down plotting. see https://www.naturalearthdata.com/
crs = ccrs.PlateCarree()  # projection. Must be a class from cartopy.crs. Note, that plotting labels does not work for most projections.
markersize = 4  # diameter of Marker in points.
map_pad = 0.15  # padding relative to map height.
grid_intervals = [0.25, 0.5, 1, 2, 5, 10, 30]  # grid spacing in degree to choose from (plotter will try to make 5 gridlines in the smaller dimension)
max_title_len = 50  # maximum length of plot title in chars. if longer, it will be broken in multiple lines.

# === boxplot defaults ===
boxplot_printnumbers = True  # Print 'median', 'nObs', 'stdDev' to the boxplot.
boxplot_figsize = [6.30, 4.68]  # size of the output figure in inches. NO MORE USED.
boxplot_height = 4.68
boxplot_width = 1.5  # times (n+1), where n is the number of boxes.
boxplot_title_len = 15  # times the number of boxes. maximum length of plot title in chars.

# === watermark defaults ===
watermark = u'made with QA4SM (qa4sm.eodc.eu)'  # Watermark string
watermark_pos = 'top'  # Default position ('top' or 'bottom')
watermark_fontsize = 10  # fontsize in points (matplotlib uses 72ppi)
watermark_pad = 5  # padding above/below watermark in points (matplotlib uses 72ppi)

# === filename template ===
ds_fn_templ = "{i}-{ds}.{var}"
ds_fn_sep = "_with_"

# === colormaps used for plotting metrics ===
# Colormaps can be set for classes of similar metrics or individually for metrics.
# Any colormap name can be used, that works with matplotlib.pyplot.cm.get_cmap('colormap')
# more on colormaps: https://matplotlib.org/users/colormaps.html | https://morphocode.com/the-use-of-color-in-maps/
# colorcet: http://colorcet.pyviz.org/user_guide/Continuous.html

import colorcet
import matplotlib.pyplot as plt
_cclasses = {
    'div_better': plt.cm.get_cmap('RdYlBu'),  # diverging: 1 good, 0 special, -1 bad (pearson's R, spearman's rho')
    'div_neutr': plt.cm.get_cmap('RdYlGn'),  # diverging: zero good, +/- neutral: (bias)
    'seq_worse': colorcet.cm['CET_L4_r'], #'cet_CET_L4_r',  # sequential: increasing value bad (p_R, p_rho, rmsd, ubRMSD, RSS):
    'seq_better': colorcet.cm['CET_L4'], #'cet_CET_L4'  # sequential: increasing value good (n_obs)
}

# 0=common metrics, 2=paired metrics (2 datasets), 3=triple metrics (TC)
metric_groups = {0 : ['n_obs'],
                 2 : ['R', 'p_R', 'rho','p_rho','RMSD', 'BIAS',
                      'urmsd', 'mse', 'mse_corr', 'mse_bias', 'mse_var',
                      'RSS', 'tau', 'p_tau'],
                 3 : ['snr', 'err_std', 'beta']}

# === variable template ===
# how the metric is separated from the rest
var_name_metric_sep = {0: "{metric}", 2: "{metric}_between_",
                       3: "{metric}_{id0}-{dataset}_between_"}
# how two datasets are separated
var_name_ds_sep = {0: None, 2: "{id1}-{dataset1}_and_{id2}-{dataset2}",
                   3: "{id1}-{dataset1}_and_{id2}-{dataset2}_and_{id3}-{dataset3}"}


_colormaps = {  # from /qa4sm/validator/validation/graphics.py
    'R': _cclasses['div_better'],
    'p_R': _cclasses['seq_worse'],
    'rho': _cclasses['div_better'],
    'p_rho': _cclasses['seq_worse'],
    'RMSD': _cclasses['seq_worse'],
    'BIAS': _cclasses['div_neutr'],
    'n_obs': _cclasses['seq_better'],
    'urmsd': _cclasses['seq_worse'],
    'mse': _cclasses['seq_worse'],
    'mse_corr': _cclasses['seq_worse'],
    'mse_bias': _cclasses['seq_worse'],
    'mse_var': _cclasses['seq_worse'],
    'RSS' : _cclasses['seq_worse'],
    'tau' :_cclasses['div_better'],
    'p_tau' : _cclasses['seq_worse'],
    'snr': _cclasses['div_better'],
    'err_std': _cclasses['div_neutr'],
    'beta': _cclasses['div_neutr'],
}
# check if every metric has a colormap
for group in metric_groups.keys():
    assert all([m in _colormaps.keys() for m in metric_groups[group]])

# Value ranges of metrics
_metric_value_ranges = {  # from /qa4sm/validator/validation/graphics.py
    'R': [-1, 1],
    'p_R': [0, 1],  # probability that observed corellation is statistical fluctuation
    'rho': [-1, 1],
    'p_rho': [0, 1],
    'RMSD': [0, None],
    'BIAS': [None, None],
    'n_obs': [0, None],
    'urmsd': [0, None],
    'RSS': [0, None],
    'mse': [0, None],  # mse only positive (https://en.wikipedia.org/wiki/Mean_squared_error)
    'mse_corr': [0, None],  # mse_corr only positive
    'mse_bias': [0, None],  # mse_bias only positive
    'mse_var': [0, None],  # mse_var only positive
    'snr': [None, None],  # mse_var only positive
    'err_std': [None, None],  # mse_var only positive
    'beta': [None, None],  # mse_var only positive
}

# check if every metric has a colormap
for group in metric_groups.keys():
    assert all([m in _colormaps.keys() for m in metric_groups[group]])

# label format for all metrics
_metric_description = {  # from /qa4sm/validator/validation/graphics.py
    'R': '',
    'p_R': '',
    'rho': '',
    'p_rho': '',
    'tau': '',
    'p_tau': '',
    'RMSD': r' in ${}$',
    'BIAS': r' in ${}$',
    'n_obs': '',
    'urmsd': r' in ${}$',
    'RSS': r' in $({})^2$',
    'mse': r' in $({})^2$',
    'mse_corr': r' in $({})^2$',
    'mse_bias': r' in $({})^2$',
    'mse_var': r' in $({})^2$',
    'snr': r' in $({})$',
    'err_std': r' in $({})$',
    'beta': r' in $({})$',
}

_ref_ds_attr = 'val_ref' # global variable that defines the reference set
_ds_short_name_attr = 'val_dc_dataset{:d}' # attribute convention for other datasets
_ds_pretty_name_attr = 'val_dc_dataset_pretty_name{:d}' # attribute convention for other datasets
_version_short_name_attr = 'val_dc_version{:d}' # attribute convention for other datasets
_version_pretty_name_attr = 'val_dc_version_pretty_name{:d}' # attribute convention for other datasets


# units for all datasets
_metric_units = {  # from /qa4sm/validator/validation/graphics.py
    'ISMN': r'm^3 m^{-3}',
    'C3S': r'm^3 m^{-3}',
    'GLDAS': r'm^3 m^{-3}',
    'ASCAT': r'percentage of saturation',
    'SMAP': r'm^3 m^{-3}',
    'ERA5': r'm^3 m^{-3}',
    'ERA5_LAND': r'm^3 m^{-3}',
    'ESA_CCI_SM_combinded': r'',
    'SMOS': r''
}

# label name for all metrics
_metric_name = {  # from /qa4sm/validator/validation/globals.py
    'R': 'Pearson\'s r',
    'p_R': 'Pearson\'s r p-value',
    'rho': 'Spearman\'s rho',
    'p_rho': 'Spearman\'s rho p-value',
    'RMSD': 'Root-mean-square deviation',
    'BIAS': 'Bias (difference of means)',
    'n_obs': '# observations',
    'urmsd': 'Unbiased root-mean-square deviation',
    'RSS': 'Residual sum of squares',
    'tau': 'Kendall rank correlation',
    'p_tau': 'Kendall tau p-value',
    'mse': 'Mean square error',
    'mse_corr': 'Mean square error correlation',
    'mse_bias': 'Mean square error bias',
    'mse_var': 'Mean square error variance',
    'snr': 'Signal-to-noise ratio',
    'err_std': 'Error standard deviation',
    'beta': 'TC scaling coefficient',
}

# === pretty names for datasets ===
# Note: ncplot.get_meta tries to retrieve pretty names from the global attributes and falls back to here.
_dataset_pretty_names = {  # from qa4sm\validator\fixtures\datasets.json
    'ISMN': r'ISMN',
    'C3S': r'C3S',
    'GLDAS': r'GLDAS',
    'ASCAT': r'H-SAF ASCAT SSM CDR',
    'SMAP': r'SMAP level 3',
    'ERA5': r'ERA5',
    'ERA5_LAND': r'ERA5-Land',
    'ESA_CCI_SM_combined': r'ESA CCI SM combined',
    'SMOS': r'SMOS IC'
}

_dataset_version_pretty_names = {  # from qa4sm\validator\fixtures\versions.json
    "C3S_V201706": "v201706",
    "SMAP_V5_PM": "v5 PM/ascending",
    "ASCAT_H113": "H113",
    "ISMN_V20180712_TEST": "20180712 testset",
    "ISMN_V20180712_MINI": "20180712 mini testset",
    "ISMN_V20180830_GLOBAL": "20180830 global",
    "GLDAS_NOAH025_3H_2_1": "NOAH025 3H.2.1",
    "GLDAS_TEST": "TEST",
    "C3S_V201812": "v201812",
    "ISMN_V20190222": "20190222 global",
    "ESA_CCI_SM_C_V04_4": "v04.4",
    "SMOS_105_ASC": "V.105 Ascending",
    "ERA5_test": "ERA5 test",
    "ERA5": "ERA5",
    "ERA5_LAND" : "ERA5-Land",
    "ERA5_LAND_TEST": "ERA5-Land Test"
}
