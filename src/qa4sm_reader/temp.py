# -*- coding: utf-8 -*-

"""
Module description
"""
# TODO:
#   (+) 
#---------
# NOTES:
#   -
class MetVar(MetricVariable):
    """ Represents a metric variable in QA4SM """

    def __init__(self, name, attrs=None):
        super(MetVar).__init__(name, attrs)
        self.metric, self.g = self._2met()
        self.parts = self._split()

    def _split(self) -> (tuple, int):
        """ split into parts and also get the metric group"""
        g = self.g
        if g == 2 or g == 3:
            pass

        elif g == 0:
            pattern = globals.var_name_metric_sep[0]
        else:
            raise NotImplementedError(g, 'Metric group {} not implemented'.format(g))

        parts = parse(pattern, self.name)
        assert parts['metric'] == self.metric
        return parts