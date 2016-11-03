import unittest
from unittest import mock
import os
import importlib
import copy

from nwpc_hpc_collector.loadleveler import query_category
from nwpc_hpc_collector.loadleveler import record_parser
from nwpc_hpc_collector.loadleveler import value_saver


class TestQueryCategory(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_deep_copy(self):
        category = query_category.QueryCategory()
        category.id = "llq.id"
        category.record_parser = record_parser.DetailLabelParser("Job Step Id")
        category.value_saver = value_saver.StringSaver()

        new_category = copy.deepcopy(category)
        new_category.id = "llq.submitted"
        new_category.record_parser.label = "Submitted"

        self.assertNotEqual(category.id, new_category.id)
        self.assertNotEqual(category.record_parser, new_category.record_parser)
        self.assertNotEqual(category.record_parser.label, new_category.record_parser.label)
