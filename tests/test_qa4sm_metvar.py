
from src.qa4sm_reader.handlers import QA4SMMetricVariable
import os
import re
import numpy as np
import unittest
from src.qa4sm_reader import globals
from tests.test_qa4sm_data import test_tc_attributes, test_attributes

class TestMetricVariableTC(unittest.TestCase):

    def setUp(self) -> None:
        attrs = test_tc_attributes()
        self.n_obs = QA4SMMetricVariable('n_obs', attrs)
        self.r = QA4SMMetricVariable('R_between_3-ERA5_LAND_and_1-C3S', attrs)
        self.beta = QA4SMMetricVariable('beta_1-C3S_between_3-ERA5_LAND_and_1-C3S_and_2-ASCAT', attrs)


class TestMetricVariableBasic(unittest.TestCase):

    def setUp(self) -> None:
        attrs = test_attributes()
        self.n_obs = QA4SMMetricVariable('n_obs', attrs)
        self.r = QA4SMMetricVariable('R_between_6-ISMN_and_4-SMAP', attrs)
        self.pr = QA4SMMetricVariable('p_rho_between_6-ISMN_and_5-ASCAT', attrs)