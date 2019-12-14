# -*- coding: utf-8 -*-

from src.qa4sm_reader.handlers import QA4SMDataAttributes
from tests.test_qa4sm_attrs import test_attributes, test_tc_attributes
import unittest

class TestDatasets(unittest.TestCase):
    def setUp(self) -> None:
        attrs = test_attributes()
        self.ismn = QA4SMDataAttributes(id=6, short_name='ISMN', global_attrs=attrs)
        self.c3s17 = QA4SMDataAttributes(id=1, short_name='C3S', global_attrs=attrs)
        self.c3s18 = QA4SMDataAttributes(id=2, short_name='C3S', global_attrs=attrs)
        self.smos = QA4SMDataAttributes(id=3, short_name='SMOS', global_attrs=attrs)
        self.smap = QA4SMDataAttributes(id=4, short_name='SMAP', global_attrs=attrs)
        self.ascat = QA4SMDataAttributes(id=5, short_name='ASCAT', global_attrs=attrs)

    def test_names(self):
        assert self.ismn.pretty_name() == 'ISMN'
        assert self.ismn.pretty_version() == '20180712 mini testset'

        assert self.c3s17.pretty_name() == 'C3S'
        assert self.c3s17.pretty_version() == 'v201706'

        assert self.c3s18.pretty_name() == 'C3S'
        assert self.c3s18.pretty_version() == 'v201812'

        assert self.smos.pretty_name() == 'SMOS IC'
        assert self.smos.pretty_version() == 'V.105 Ascending'

        assert self.smap.pretty_name() == 'SMAP level 3'
        assert self.smap.pretty_version() == 'v5 PM/ascending'

        assert self.ascat.pretty_name() == 'H-SAF ASCAT SSM CDR'
        assert self.ascat.pretty_version() == 'H113'


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestDatasets("test_get_ref_name"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
