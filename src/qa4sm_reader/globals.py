# -*- coding: utf-8 -*-


__author__ = "Lukas Racbhauer"
__copyright__ = "2019, TU Wien, Department of Geodesy and Geoinformation"
__license__ = "mit"


"""
Global variables collected from different sources.
"""

import cartopy.crs as ccrs  # TODO: is it meaningful to create prjojection objects here?

# === from qa4sm.validator.validation.graphics ===

_metric_value_ranges = {  # from /qa4sm/validator/validation/graphics.py
    'R': [-1, 1],
    'p_R': [0, 1],  # probability that observed corellation is statistical fluctuation
    'rho': [-1, 1],
    'p_rho': [0, 1],
    # probability that observed corellation is statistical fluctuation (probability of null hypothesis: there is no correlation)
    'rmsd': [0, None],
    'bias': [None, None],
    'n_obs': [0, None],
    'ubRMSD': [0, None],
    'RSS': [0, None],
    'mse': [0, None],  # mse only positive (https://en.wikipedia.org/wiki/Mean_squared_error)
    'mse_corr': [0, None],  # mse_corr only positive
    'mse_bias': [0, None],  # mse_bias only positive
    'mse_var': [0, None],  # mse_var only positive
}

# label format for all metrics
_metric_description = {  # from /qa4sm/validator/validation/graphics.py
    'R': '',
    'p_R': '',
    'rho': '',
    'p_rho': '',
    'rmsd': r' in ${}$',
    'bias': r' in ${}$',
    'n_obs': '',
    'ubRMSD': r' in ${}$',
    'RSS': r' in $({})^2$',
    'mse': r' in $({})^2$',
    'mse_corr': r' in $({})^2$',
    'mse_bias': r' in $({})^2$',
    'mse_var': r' in $({})^2$',
}

# units for all datasets
_metric_units = {  # from /qa4sm/validator/validation/graphics.py
    'ISMN': r'm^3 m^{-3}',
    'C3S': r'm^3 m^{-3}',
    'GLDAS': r'm^3 m^{-3}',
    'ASCAT': r'percentage of saturation',
    'SMAP': r'm^3 m^{-3}',
    'ERA5': r'm^3 m^{-3}',
    'ERA': r'm^3 m^{-3}',  # by mistake, the dataset was called like this for some time.
    'ESA_CCI_SM_combinded': r'',
    'SMOS': r''
}

# === from qa4sm.validator.validation.globals ===

# label name for all metrics
_metric_name = {  # from /qa4sm/validator/validation/globals.py
    'R': 'Pearson\'s r',
    'p_R': 'Pearson\'s r p-value',
    'rho': 'Spearman\'s rho',
    'p_rho': 'Spearman\'s rho p-value',
    'rmsd': 'Root-mean-square deviation',
    'bias': 'Bias (difference of means)',
    'n_obs': '# observations',
    'ubRMSD': 'Unbiased root-mean-square deviation',
    'RSS': 'Residual sum of squares',
    'mse': 'Mean square error',
    'mse_corr': 'Mean square error correlation',
    'mse_bias': 'Mean square error bias',
    'mse_var': 'Mean square error variance',
}

# colormaps used for plotting metrics
# more on colormaps: https://matplotlib.org/users/colormaps.html | https://morphocode.com/the-use-of-color-in-maps/
# colorcet: http://colorcet.pyviz.org/user_guide/Continuous.html

_cclasses = {
    'div_better': 'RdYlBu',
    # diverging: 1 good, 0 special, -1 bad (pearson's R, spearman's rho') 'cet_coolwarm_r', 'cet_CET_D8_r'],
    'div_neutr': 'RdYlGn',
    # diverging: zero good, +/- neutral: (bias):  'Spectral', 'cet_CET_D3', 'cet_gwv', 'cet_bwy', 'cet_bjy'],
    'seq_worse': 'cet_CET_L4_r',  # sequential: increasing value bad (p_R, p_rho, rmsd, ubRMSD, RSS, ):
    'seq_better': 'cet_CET_L4'  # sequential: increasing value good (n_obs):
}

_colormaps = {  # from /qa4sm/validator/validation/graphics.py
    'R': _cclasses['div_better'],
    'p_R': _cclasses['seq_worse'],
    'rho': _cclasses['div_better'],
    'p_rho': _cclasses['seq_worse'],
    'rmsd': _cclasses['seq_worse'],
    'bias': _cclasses['div_neutr'],
    'n_obs': _cclasses['seq_better'],
    'ubRMSD': _cclasses['seq_worse'],
    'mse': _cclasses['seq_worse'],
    'mse_corr': _cclasses['seq_worse'],
    'mse_bias': _cclasses['seq_worse'],
    'mse_var': _cclasses['seq_worse'],
}

# === pretty names ===
# pretty names for all datasets
_dataset_pretty_names = {  # from qa4sm\validator\fixtures\datasets.json
    'ISMN': r'ISMN',
    'C3S': r'C3S',
    'GLDAS': r'GLDAS',
    'ASCAT': r'H-SAF ASCAT SSM CDR',
    'SMAP': r'SMAP level 3',
    'ERA5': r'ERA5',
    'ERA': r'ERA5',  # by mistake, the dataset was called like this for some time.
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
    "ERA5": "ERA5"
}

# === plot defaults ===
matplotlib_ppi = 72
index_names = ['lat', 'lon']
dpi = 100
max_title_len = 50  # maximum length of plot title in chars. if longer, it will be broken in multiple lines.
title_pad = 12.0  # in points. default padding is matplotlib.rcParams['axes.titlepad'] = 6.0
data_crs = ccrs.PlateCarree()

# === map plot defaults ===
scattered_datasets = ['ISMN']  # dataset names which require scatterplots (data is scattered in lat/lon)
map_figsize = [11.32, 6.10]
naturalearth_resolution = '110m'  # choose from '10m', '50m' and '110m'
crs = ccrs.PlateCarree()
markersize = 4  # diameter in points.
map_pad = 0.15  # padding relative to map height.
grid_intervals = [0.25, 0.5, 1, 2, 5, 10,
                  30]  # grid delta to choose from (plotter will try to make 5 gridlines in the smaller dimension)

# === boxplot defaults ===
boxplot_printnumbers = True
boxplot_figsize = [6.30, 4.68]

# === watermark defaults ===
watermark = u'made with QA4SM (qa4sm.eodc.eu)'
watermark_pos = 'top'
watermark_fontsize = 10  # in points
watermark_pad = 5  # in points (matplotlib uses 72ppi)
