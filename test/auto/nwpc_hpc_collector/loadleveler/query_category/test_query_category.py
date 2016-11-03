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

    def test_create_query_category(self):
        id_category = query_category.QueryCategory(
            category_id="llq.id",
            display_name="Id",
            label="Job Step Id",
            record_parser_class=record_parser.DetailLabelParser,
            record_parser_arguments=("Job Step Id",),
            value_saver_class=value_saver.StringSaver
        )

        self.assertEqual(id_category.id, "llq.id")
        self.assertEqual(id_category.display_name, "Id")
        self.assertEqual(id_category.label, "Job Step Id")
        self.assertIsInstance(id_category.record_parser, record_parser.DetailLabelParser)
        self.assertEqual(id_category.record_parser.label, "Job Step Id")
        self.assertIsInstance(id_category.value_saver, value_saver.StringSaver)
