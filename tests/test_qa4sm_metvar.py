# -*- coding: utf-8 -*-

from qa4sm_reader.handlers import QA4SMMetricVariable
import unittest
from tests.test_qa4sm_attrs import test_tc_attributes, test_attributes
import pandas as pd

class TestMetricVariableTC(unittest.TestCase):

    def setUp(self) -> None:
        attrs = test_tc_attributes()
        df_nobs = pd.DataFrame(index=range(10), data={'n_obs': range(10)})
        self.n_obs = QA4SMMetricVariable('n_obs', attrs, values=df_nobs)
        self.r = QA4SMMetricVariable('R_between_3-ERA5_LAND_and_1-C3S', attrs)
        self.beta = QA4SMMetricVariable('beta_1-C3S_between_3-ERA5_LAND_and_1-C3S_and_2-ASCAT', attrs)

    def test_get_varmeta(self):
        # n_obs
        assert self.n_obs.ismetr()
        assert not self.n_obs.isempty()
        ref, dss, mds = self.n_obs.get_varmeta()
        assert ref[1]['short_name'] == 'ERA5_LAND'
        assert dss == mds is None

        # R
        ref, dss, mds = self.r.get_varmeta()
        assert ref[0] == 3
        assert ref[1]['short_name'] == 'ERA5_LAND'
        assert ref[1]['pretty_name'] == 'ERA5-Land'
        assert ref[1]['short_version'] == 'ERA5_LAND_TEST'
        assert ref[1]['pretty_version'] == 'ERA5-Land test'

        assert len(dss) == 1
        assert dss[0][0] == 1
        ds_meta = dss[0][1]
        assert ds_meta['short_name'] == 'C3S'
        assert ds_meta['pretty_name'] == 'C3S'
        assert ds_meta['short_version'] == 'C3S_V201812'
        assert ds_meta['pretty_version'] == 'v201812'
        assert mds is None

        # p
        ref, dss, mds = self.beta.get_varmeta()
        assert ref[0] == 3
        assert ref[1]['short_name'] == 'ERA5_LAND'
        assert ref[1]['pretty_name'] == 'ERA5-Land'
        assert ref[1]['short_version'] == 'ERA5_LAND_TEST'
        assert ref[1]['pretty_version'] == 'ERA5-Land test'

        assert len(dss) == 2
        assert dss[0][0] == 1
        assert dss[1][0] == 2
        ds1_meta = dss[0][1]
        ds2_meta = dss[1][1]
        assert ds1_meta['short_name'] == 'C3S'
        assert ds1_meta['pretty_name'] == 'C3S'
        assert ds1_meta['short_version'] == 'C3S_V201812'
        assert ds1_meta['pretty_version'] == 'v201812'
        assert ds2_meta['short_name'] == 'ASCAT'
        assert ds2_meta['pretty_name'] == 'H-SAF ASCAT SSM CDR'
        assert ds2_meta['short_version'] == 'ASCAT_H113'
        assert ds2_meta['pretty_version'] == 'H113'

        assert mds[0] == 1
        mds_meta = mds[1]
        assert mds_meta['short_name'] == 'C3S'
        assert mds_meta['pretty_name'] == 'C3S'
        assert mds_meta['short_version'] == 'C3S_V201812'
        assert mds_meta['pretty_version'] == 'v201812'

class TestMetricVariableBasic(unittest.TestCase):

    def setUp(self) -> None:
        attrs = test_attributes()
        df_nobs = pd.DataFrame(index=range(10), data={'n_obs': range(10)})
        self.n_obs = QA4SMMetricVariable('n_obs', attrs, values=df_nobs)

        self.r = QA4SMMetricVariable('R_between_6-ISMN_and_4-SMAP', attrs)
        self.pr = QA4SMMetricVariable('p_rho_between_6-ISMN_and_5-ASCAT', attrs)

    def test_get_varmeta(self):
        # n_obs
        assert self.n_obs.ismetr()
        assert not self.n_obs.isempty()
        # todo: use the names from metadata?
        ref, dss, mds = self.n_obs.get_varmeta()
        assert ref[1]['short_name'] == 'ISMN'
        assert dss == mds is None

        # R
        ref, dss, mds = self.r.get_varmeta()
        assert ref[0] == 6
        assert ref[1]['short_name'] == 'ISMN'
        assert ref[1]['pretty_name'] == 'ISMN'
        assert ref[1]['short_version'] == 'ISMN_V20180712_MINI'
        assert ref[1]['pretty_version'] == '20180712 mini testset'
        assert dss[0][0] == 4
        assert len(dss) == 1
        ds_meta = dss[0][1]
        assert ds_meta['short_name'] == 'SMAP'
        assert ds_meta['pretty_name'] == 'SMAP level 3'
        assert ds_meta['short_version'] == 'SMAP_V5_PM'
        assert ds_meta['pretty_version'] == 'v5 PM/ascending'
        assert mds is None

        # p
        ref, dss, mds = self.pr.get_varmeta()
        assert ref[0] == 6
        assert ref[1]['short_name'] == 'ISMN'
        assert ref[1]['pretty_name'] == 'ISMN'
        assert ref[1]['short_version'] == 'ISMN_V20180712_MINI'
        assert ref[1]['pretty_version'] == '20180712 mini testset'
        assert dss[0][0] == 5
        assert len(dss) == 1
        ds_meta = dss[0][1]
        assert ds_meta['short_name'] == 'ASCAT'
        assert ds_meta['pretty_name'] == 'H-SAF ASCAT SSM CDR'
        assert ds_meta['short_version'] == 'ASCAT_H113'
        assert ds_meta['pretty_version'] == 'H113'
        assert mds is None

if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestSuite()
    # suite.addTest(TestMetricVariableTC("test_get_varmeta"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)