# -*- coding: utf-8 -*-
'''
Contains plotting routines that take pd.DataFrames and metadata dictionaries 
as input and return figure and axes objects.
'''
import globals

import numpy as np

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

import time

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
    ax.set_ylim(globals._metric_value_ranges[metric])
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
    if watermark_pos: print_watermark(fig,watermark_pos)
    return fig,ax

def scatterplot(df, var, meta, llc=None, urc=None, add_cbar=True,
                figsize=globals.map_figsize, dpi=globals.dpi,
                projection = globals.crs, watermark_pos=globals.watermark_pos,
                title_pad = globals.title_pad, add_grid = True,
                add_rendering=True, add_coastline = True, add_land = True,
                add_borders = True, add_us_states = False):
    ## start=time.time()
    # === value range ===
    v_min = globals._metric_value_ranges[meta['metric']][0]
    v_max = globals._metric_value_ranges[meta['metric']][1]
    if v_min == None and v_max == None: #make sure the range is symmetrical
        v_max = df[var].abs().max()
        v_min = -v_max

    # === coordiniate range ===
    try:
        extent = [llc[0],urc[0],llc[1],urc[1]]
    except:
        extent = [df['lon'].min(), df['lon'].max(),
              df['lat'].min(), df['lat'].max()]
        lon_interval = extent[1] - extent[0]
        lat_interval = extent[3] - extent[2]
        #set map-padding around data to be globals.map_pad percent of the smaller dimension
        padding = min([lon_interval,lat_interval]) * globals.map_pad/(1+globals.map_pad)
        extent = [extent[0] - padding, #x_min / lon_min
                  extent[1] + padding, #x_max / lon_max
                  extent[2] - padding, #y_min / lat_min
                  extent[3] + padding] #y_max / lat_max

    lon_interval = extent[1] - extent[0]
    lat_interval = extent[3] - extent[2]
    print(extent)

    # === marker size ===
    markersize = globals.markersize**2 #in points**2
    ## print('{}s\ninitializing plot...'.format(time.time()-start))
    # === init plot ===
    if add_cbar:
        gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[19,1])
    else:
        gs = gridspec.GridSpec(nrows=1, ncols=1)
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(gs[0],projection=projection)

    ## print('{}s\nstarting to plot...'.format(time.time()-start))
    # === plot ===
    cm = plt.cm.get_cmap(globals._colormaps[meta['metric']])
    im = ax.scatter(df['lon'], df['lat'], c=df[var],
            cmap=cm, s=markersize, vmin=v_min, vmax=v_max, edgecolors='black',
            linewidths=0.1, zorder=4, transform=globals.data_crs)
    ax.set_extent(extent, crs=globals.data_crs)
    ## print('{}s\nsetting style...'.format(time.time()-start))

    # === style ===
    ax.outline_patch.set_linewidth(0.4)
    if add_rendering: ax.stock_img()
    if add_coastline:
        coastline = cfeature.NaturalEarthFeature('physical', 'coastline',
                                 globals.naturalearth_resolution,
                                 edgecolor='black', facecolor='none')
        ax.add_feature(coastline, linewidth=0.4, zorder=2)
    if add_land:
        land = cfeature.NaturalEarthFeature('physical', 'land',
                                 globals.naturalearth_resolution,
                                 edgecolor='none', facecolor='white')
        ax.add_feature(land, zorder=1)
    if add_borders:
        borders = cfeature.NaturalEarthFeature('cultural', 'admin_0_countries',
                                 globals.naturalearth_resolution,
                                 edgecolor='black', facecolor='none')
        ax.add_feature(borders, linewidth=0.2, zorder=2)
    if add_us_states: ax.add_feature(cfeature.STATES, linewidth=0.1, zorder=2)
    ## print('{}s\nadding gridlines...'.format(time.time()-start))
    if add_grid: # add gridlines
        grid_interval = max(lon_interval,lat_interval)/5 #create approximately 4 gridlines in the bigger dimension
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
            xticks = xticks[(xticks>=extent[0]) & (xticks<=extent[1])]
            yticks = yticks[(yticks>=extent[2]) & (yticks<=extent[3])]
            gltext.xformatter=LONGITUDE_FORMATTER
            gltext.yformatter=LATITUDE_FORMATTER
            gltext.xlabels_top=False
            gltext.ylabels_left=False
            gltext.xlocator = mticker.FixedLocator(xticks)
            gltext.ylocator = mticker.FixedLocator(yticks)
        except RuntimeError as e:
            print("No tick labels plotted.\n" + str(e))

    # === add colorbar ===
    ## print('{}s\nadding colorbar...'.format(time.time()-start))
    if add_cbar:
        cax = fig.add_subplot(gs[1])
        cbar = fig.colorbar(im, cax=cax, orientation='horizontal')
        cbar.set_label(globals._metric_name[meta['metric']] + globals._metric_description[meta['metric']].format(globals._metric_units[meta['ref']])) #, size=5)
        cbar.outline.set_linewidth(0.4)
        cbar.outline.set_edgecolor('black')
        cbar.ax.tick_params(width=0.4)#, labelsize=4)
    ## print('{}s\nadding title...'.format(time.time()-start))

    plot_title = 'Comparing {0} ({1}) to {2} ({3})'.format(
                meta['ref_pretty_name'],
                meta['ref_version_pretty_name'],
                meta['ds_pretty_name'],
                meta['ds_version_pretty_name'])
    ax.set_title(plot_title)
    ## print('{}s\ndrawing...'.format(time.time()-start))

    # === watermark ===
    #debug_tight_layout(fig)
    #debug_tight_layout_gs(fig,gs)
    fig.canvas.draw() #nötig wegen bug in cartopy. dauert sehr lange!
    ## print('{}s\ntight layout...'.format(time.time()-start))
    plt.tight_layout(pad=1) #pad=0.5,h_pad=1,w_pad=1,rect=(0, 0, 1, 1))
    ## print('{}s\nwatermark...'.format(time.time()-start))
    if watermark_pos: print_watermark(fig,watermark_pos)
    ## print('{}s\nfinished.'.format(time.time()-start))

    return fig,ax

def print_watermark(fig,placement):
    """
    Adds a watermark to fig and adjusts the current axis to make sure there
    is enough padding around the watermarks.
    Padding can be adjusted in globals.watermark_pad.
    Fontsize can be adjusted in globals.watermark_fontsize.
    plt.tight_layout needs to be called prior to print_watermark

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