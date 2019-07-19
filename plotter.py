# -*- coding: utf-8 -*-
'''
Contains plotting routines that take pd.DataFrames and metadata dictionaries 
as input and return figure and axes objects.
'''
import globals

import numpy as np
import pandas as pd

import os.path

import seaborn as sns

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec

from cartopy import config as cconfig
cconfig['data_dir'] = os.path.join(os.path.dirname(__file__), 'cartopy')
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

import warnings

def boxplot(df, varmeta, globmeta, printnumbers=globals.boxplot_printnumbers,
            watermark_pos=globals.watermark_pos, figsize=globals.boxplot_figsize,
            dpi=globals.dpi, title_pad = globals.title_pad):
    """returns fig, ax object of boxplot.
    Labels come from df. Other labelling comes from varmeta and globmeta, 
    referring to names stored in global variables in globals
    """
    # === drop lat lon ===
    try:
        df.drop(columns=globals.index_names, inplace=True)
    except KeyError:
        pass
    # === rename columns = label of box ===
    if printnumbers:
        # === calculate mean, std dev, Nobs ===
        for var in varmeta:
            varmeta[var]['median'] = df[var].median()
            varmeta[var]['stddev'] = df[var].std()
            varmeta[var]['Nobs'] = df[var].count()
        # === rename columns before plotting ===
        df.columns = ['{0}\n({1})\nmedian: {2:.3g}\nstd. dev.: {3:.3g}\nN obs.: {4:d}'.format(
                varmeta[var]['ds_pretty_name'],
                varmeta[var]['ds_version_pretty_name'],
                varmeta[var]['median'],
                varmeta[var]['stddev'],
                varmeta[var]['Nobs']) for var in varmeta]
    else:
        df.columns = ['{}\n{}'.format(
                varmeta[var]['ds_pretty_name'],
                varmeta[var]['ds_version_pretty_name']) for var in varmeta]

    # === plot ===
    fig,ax = plt.subplots(figsize=figsize, dpi=dpi) #tight_layout = True,
    sns.set_style("whitegrid")
    ax = sns.boxplot(data=df, ax=ax, width=0.15, showfliers=False, color='white')
    sns.despine()

    # === style ===
    metric=globmeta['metric']
    ax.set_ylim(get_value_range(df, metric))
    ax.set_ylabel(globals._metric_name[metric] +
                  globals._metric_description[metric].format(globals._metric_units[globmeta['ref']]))
    # === generate title with automatic line break ===
    plot_title = list() #each list element is a line in the plot title
    plot_title.append('Comparing {} to '.format(globmeta['ref_pretty_name']))
    for var in varmeta:
        to_append = '{}, '.format(varmeta[var]['ds_pretty_name'])
        if len(plot_title[-1] + to_append) <= globals.max_title_len: #line not to long: add to current line
            plot_title[-1] += to_append
        else: #add to next line
            plot_title.append(to_append)
    plot_title = '\n'.join(plot_title)[:-2] #join lines together and remove last ', '
    plot_title = ' and '.join(plot_title.rsplit(', ',1)) #replace last ', ' with ' and '
    ax.set_title(plot_title, pad=title_pad)
    # === watermark ===
    plt.tight_layout()
    if watermark_pos: make_watermark(fig,watermark_pos)
    return fig,ax

def scatterplot(df, var, meta, title=None, label=None, llc=None, urc=None,
                figsize=globals.map_figsize, dpi=globals.dpi,
                projection = None, watermark_pos=globals.watermark_pos,
                add_title = True, add_cbar=True,
                **style_kwargs):
    # === value range ===
    v_min, v_max = get_value_range(df[var], meta['metric'])

    # === coordiniate range ===
    cr = get_coordinate_range(df, llc, urc)

    # === marker size ===
    markersize = globals.markersize**2 #in points**2

    # === init plot ===
    fig, ax, cax = init_plot(figsize, dpi, add_cbar)

    # === plot ===
    cmap = plt.cm.get_cmap(globals._colormaps[meta['metric']])
    lat, lon = globals.index_names
    im = ax.scatter(df[lon], df[lat], c=df[var],
            cmap=cmap, s=markersize, vmin=v_min, vmax=v_max, edgecolors='black',
            linewidths=0.1, zorder=4, transform=globals.data_crs)

    # === add colorbar ===
    if add_cbar: _make_cbar(fig, im, cax, df[var], v_min, v_max, meta, label)

    # === style ===
    if add_title: _make_title(ax, meta, title)
    style_map(ax, cr, **style_kwargs)

    # === layout ===
    fig.canvas.draw() #nötig wegen bug in cartopy. dauert sehr lange!
    plt.tight_layout(pad=1) #pad=0.5,h_pad=1,w_pad=1,rect=(0, 0, 1, 1))

    # === watermark ===
    if watermark_pos: make_watermark(fig,watermark_pos) #tight_layout does not take into account annotations, so make_watermark needs to be called after.

    return fig,ax

def get_value_range(ds, metric=None, force_quantile=False, quantiles=[0.025,0.975]):
    """
    Get the value range (v_min, v_max) from globals._metric_value_ranges
    If the range is (None, None), a symmetric range around 0 is created,
    showing at least the symmetric <quantile> quantile of the data. 
    if force_quantile is True, the quantile range is used.

    Parameters
    ----------
    ds : (pandas.Series | pandas.DataFrame)
        Series holding the data
    metric : (str | None), optional
        name of the metric (e.g. 'R'). None equals to force_quantile=True.
        The default is None.
    force_quantile : bool, optional
        always use quantile, regardless of globals.
        The default is False.
    quantiles : list, optional
        quantile of data to include in the range.
        The default is [0.025,0.975]

    Returns
    -------
    v_min : float
        lower value range of plot.
    v_max : float
        upper value range of plot.
    extend : str
        whether the data extends further than the computed range.
        one of ['neither', 'min', 'max', 'both']

    """
    if metric == None: force_quantile=True
    if not force_quantile: #try to get range from globals
        try:
            v_min = globals._metric_value_ranges[metric][0]
            v_max = globals._metric_value_ranges[metric][1]
            if (v_min == None and v_max == None): #get quantile range and make symmetric around 0.
                v_min, v_max = get_quantiles(ds,quantiles)
                v_max = max(abs(v_min),abs(v_max)) #make sure the range is symmetric around 0
                v_min = -v_max
        except KeyError: #metric not known, fall back to quantile
            force_quantile = True
            warnings.warn('The metric \'{}\' is not known. \n'.format(metric) + \
                          'Could not get value range from globals._metric_value_ranges\n' + \
                          'Computing quantile range \'{}\' instead.\n'.format(str(quantiles)) +
                          'Known metrics are: \'' + \
                          '\', \''.join([metric for metric in globals._metric_value_ranges]) + '\'')

    if force_quantile: #get quantile range
        v_min, v_max = get_quantiles(ds,quantiles)

    return v_min, v_max

def get_quantiles(ds,quantiles):
    """
    Gets lower and upper quantiles from pandas.Series or pandas.DataFrame

    Parameters
    ----------
    ds : (pandas.Series | pandas.DataFrame)
        Input data.
    quantiles : list, optional (default: [0.025,0.975])
        quantile of data to include in the range

    Returns
    -------
    v_min : float
        lower quantile.
    v_max : float
        upper quantile.

    """
    q = ds.quantile(quantiles)
    if isinstance(ds,pd.Series):
        return q.iloc[0], q.iloc[1]
    elif isinstance(ds,pd.DataFrame):
        return min(q.iloc[0]), max(q.iloc[1])
    else:
        raise TypeError("Inappropriate argument type. 'ds' must be pandas.Series or pandas.DataFrame.")

def get_coordinate_range(df, llc=None, urc=None):
    """
    Gets the coordinate range dictionary. Tries to use urc and llc.
    Otherwise uses range of data and adds a padding fraction as specified in globals.map_pad

    Parameters
    ----------
    df : pandas.DataFrame
        Plot data.
    llc : (Array-like | None), optional
        Lower left corner in map coordinates. The default is None.
    urc : (Array-like | None), optional
        Upper right corner in map coordinates. The default is None.

    Returns
    -------
    cr : dict
        dictionary containing ['x_min', 'x_max', 'y_min', 'y_max'] in map coordinates.

    """
    try:
        cr = {'x_min' : llc[0],
              'x_max' : urc[0],
              'y_min' : llc[1],
              'y_max' : urc[1]}
    except:
        lat,lon = globals.index_names
        cr = {'x_min' : df[lon].min(),
              'x_max' : df[lon].max(),
              'y_min' : df[lat].min(),
              'y_max' : df[lat].max()}
        dx = cr['x_max'] - cr['x_min']
        dy = cr['y_max'] - cr['y_min']
        #set map-padding around data to be globals.map_pad percent of the smaller dimension
        padding = min(dx,dy) * globals.map_pad/(1+globals.map_pad)
        cr['x_min'] -= padding
        cr['x_max'] += padding
        cr['y_min'] -= padding
        cr['y_max'] += padding
    return cr

def init_plot(figsize, dpi, add_cbar, projection=globals.crs):
    fig = plt.figure(figsize=figsize, dpi=dpi)
    if add_cbar:
        gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[19,1])
        ax = fig.add_subplot(gs[0],projection=projection)
        cax = fig.add_subplot(gs[1])
    else:
        gs = gridspec.GridSpec(nrows=1, ncols=1)
        ax = fig.add_subplot(gs[0],projection=projection)
        cax = None
    return fig, ax, cax

def get_extend(ds, v_min, v_max):
    """
    whether the data extends further than v_min, v_max.  

    Parameters
    ----------
    ds : pandas.Series
        Series holding the data.
    v_min : float
        lower value range of plot.
    v_max : float
        upper value range of plot.

    Returns
    -------
    str
        one of ['neither', 'min', 'max', 'both'].

    """
    if v_min <= min(ds):
        if v_max >= max(ds):
            return 'neither'
        else:
            return 'max'
    else:
        if v_max >= max(ds):
            return 'min'
        else:
            return 'both'

def _make_cbar(fig, im, cax, ds, v_min, v_max, meta, label=None):
    if not label:
        try:
            label = globals._metric_name[meta['metric']] + \
                        globals._metric_description[meta['metric']].format(
                                globals._metric_units[meta['ref']])
        except KeyError as e:
            raise Exception('The metric \'{}\' or reference \'{}\' is not known.\n'.format(meta['metric'], meta['ref']) + str(e))
    cbar = fig.colorbar(im, cax=cax, orientation='horizontal',
                        extend=get_extend(ds,v_min,v_max))
    cbar.set_label(label) #, size=5)
    cbar.outline.set_linewidth(0.4)
    cbar.outline.set_edgecolor('black')
    cbar.ax.tick_params(width=0.4)#, labelsize=4)

def _make_title(ax, meta=None, title=None, title_pad=globals.title_pad):
    if not title:
        try:
            title = 'Comparing {0} ({1}) to {2} ({3})'.format(
                meta['ref_pretty_name'],
                meta['ref_version_pretty_name'],
                meta['ds_pretty_name'],
                meta['ds_version_pretty_name'])
        except TypeError:
            raise Exception('Either \'meta\' or \'title\' need to be specified!')
    ax.set_title(title, pad=title_pad)


def style_map(ax, cr, add_grid=True, map_resolution=globals.naturalearth_resolution,
              add_topo=True, add_coastline=True,
              add_land=True, add_borders=True, add_us_states=False):
    ax.set_extent([cr['x_min'], cr['x_max'], cr['y_min'], cr['y_max']], crs=globals.data_crs)
    ax.outline_patch.set_linewidth(0.4)
    if add_grid: # add gridlines
        grid_interval = max((cr['x_max'] - cr['x_min']),
                            (cr['y_max'] - cr['y_min']))/5 #create approximately 4 gridlines in the bigger dimension
        grid_interval = min(globals.grid_intervals, key = lambda x:abs(x-grid_interval)) #select the grid spacing from the list which fits best
        gl = ax.gridlines(crs=globals.data_crs, draw_labels=False,
                          linewidth=0.5, color='grey', linestyle='--',
                          zorder=3)
        xticks = np.arange(-180,180.001,grid_interval)
        yticks = np.arange(-90,90.001,grid_interval)
        gl.xlocator = mticker.FixedLocator(xticks)
        gl.ylocator = mticker.FixedLocator(yticks)
        try: #drawing labels fails for most projections
            gltext = ax.gridlines(crs=globals.data_crs, draw_labels=True,
                          linewidth=0.5, color='grey', alpha=0., linestyle='--',
                          zorder=3)
            xticks = xticks[(xticks>=cr['x_min']) & (xticks<=cr['x_max'])]
            yticks = yticks[(yticks>=cr['y_min']) & (yticks<=cr['y_max'])]
            gltext.xformatter=LONGITUDE_FORMATTER
            gltext.yformatter=LATITUDE_FORMATTER
            gltext.xlabels_top=False
            gltext.ylabels_left=False
            gltext.xlocator = mticker.FixedLocator(xticks)
            gltext.ylocator = mticker.FixedLocator(yticks)
        except RuntimeError as e:
            print("No tick labels plotted.\n" + str(e))
    if add_topo: ax.stock_img()
    if add_coastline:
        coastline = cfeature.NaturalEarthFeature('physical', 'coastline',
                                 map_resolution,
                                 edgecolor='black', facecolor='none')
        ax.add_feature(coastline, linewidth=0.4, zorder=2)
    if add_land:
        land = cfeature.NaturalEarthFeature('physical', 'land',
                                 map_resolution,
                                 edgecolor='none', facecolor='white')
        ax.add_feature(land, zorder=1)
    if add_borders:
        borders = cfeature.NaturalEarthFeature('cultural', 'admin_0_countries',
                                 map_resolution,
                                 edgecolor='black', facecolor='none')
        ax.add_feature(borders, linewidth=0.2, zorder=2)
    if add_us_states: ax.add_feature(cfeature.STATES, linewidth=0.1, zorder=2)



def make_watermark(fig,placement):
    """
    Adds a watermark to fig and adjusts the current axis to make sure there
    is enough padding around the watermarks.
    Padding can be adjusted in globals.watermark_pad.
    Fontsize can be adjusted in globals.watermark_fontsize.
    plt.tight_layout needs to be called prior to make_watermark

    Parameters
    ----------
    fig : matplotlib.figure.Figure
    placement : str
        'top' : places watermark in top right corner
        'bottom' : places watermark in bottom left corner

    Returns
    -------
    None.

    """
    #ax = fig.gca()
    #pos1 = ax.get_position() #fraction of figure
    fontsize = globals.watermark_fontsize
    pad = globals.watermark_pad
    height = fig.get_size_inches()[1]
    offset = ((fontsize+pad)/globals.matplotlib_ppi)/height
    if placement == 'top':
        plt.annotate(s=globals.watermark, xy = [1,1], xytext = [-pad,-pad],
                     fontsize=fontsize, color='grey',
                     horizontalalignment='right', verticalalignment='top',
                     xycoords = 'figure fraction', textcoords = 'offset points')
        #pos2 = matplotlib.transforms.Bbox.from_extents(pos1.x0, pos1.y0, pos1.x1, pos1.y1-offset)
        #ax.set_position(pos2) #todo: rather use fig.subplots_adjust
        top=fig.subplotpars.top
        fig.subplots_adjust(top=top-offset)
    elif placement == 'bottom':
        plt.annotate(s=globals.watermark, xy = [0,0], xytext = [pad,pad],
                     fontsize=fontsize, color='grey',
                     horizontalalignment='left', verticalalignment='bottom',
                     xycoords = 'figure fraction', textcoords = 'offset points')
        #pos2 = matplotlib.transforms.Bbox.from_extents(pos1.x0, pos1.y0+offset, pos1.x1, pos1.y1)
        #ax.set_position(pos2) #todo: rather use fig.subplots_adjust
        bottom=fig.subplotpars.bottom
        fig.subplots_adjust(bottom=bottom+offset) #defaults to rc when none!
    else:
        pass

def debug_tight_layout_gs(fig,gs):
    try:
        print('space before tight_layout\n   top: {:.3f}, bottom: {:.3f}, left: {:.3f}, right: {:.3f}'.format(
            1-gs.top, gs.bottom,
            gs.left, 1-gs.right))
    except:
        pass
    fig.canvas.draw() #recessary due to a bug in cartopy (https://github.com/SciTools/cartopy/issues/1207#issuecomment-439966984)
    gs.tight_layout(fig, pad=1)
    print('space after tight_layout\n   top: {:.3f}, bottom: {:.3f}, left: {:.3f}, right: {:.3f}'.format(
            1-gs.top, gs.bottom,
            gs.left, 1-gs.right))
    print('spacing if using fontsize as padding\n   left/right: {:.3f}, top/bottom: {:.3f}'.format(
            *(matplotlib.rcParams['font.size'] / 72) / fig.get_size_inches()))

def debug_tight_layout(fig):
    print('space before tight_layout\n   top: {:.3f}, bottom: {:.3f}, left: {:.3f}, right: {:.3f}'.format(
        1-fig.subplotpars.top, fig.subplotpars.bottom,
        fig.subplotpars.left, 1-fig.subplotpars.right))
    fig.canvas.draw() #recessary due to a bug in cartopy (https://github.com/SciTools/cartopy/issues/1207#issuecomment-439966984)
    plt.tight_layout(pad=1)
    print('space after tight_layout\n   top: {:.3f}, bottom: {:.3f}, left: {:.3f}, right: {:.3f}'.format(
            1-fig.subplotpars.top, fig.subplotpars.bottom,
            fig.subplotpars.left, 1-fig.subplotpars.right))
    print('spacing if using fontsize as padding\n   left/right: {:.3f}, top/bottom: {:.3f}'.format(
            *(matplotlib.rcParams['font.size'] / 72) / fig.get_size_inches()))

import plotter_usecases #for debugging
if __name__ == '__main__':
    plotter_usecases.usecase()