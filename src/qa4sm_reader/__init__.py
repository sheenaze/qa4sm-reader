# -*- coding: utf-8 -*-


__author__ = "Lukas Racbhauer"
__copyright__ = "Lukas Racbhauer"
__license__ = "mit"


from pkg_resources import get_distribution, DistributionNotFound
from qa4sm_reader import ncplot

__all__ = ['ncplot']

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound

