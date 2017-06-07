import unittest
from unittest import mock
import os
import importlib
import copy

from nwpc_hpc_model.loadleveler import query_category
from nwpc_hpc_model.loadleveler import record_parser
from nwpc_hpc_model.loadleveler import value_saver


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

    def test_llq_detail_category_list(self):
        category_list = query_category.QueryCategoryList()

        category_list.extend([
            query_category.QueryCategory("llq.id",          "Id",           "Job Step Id",
                                         record_parser.DetailLabelParser, ("Job Step Id",),
                                         value_saver.StringSaver,    ()),
            query_category.QueryCategory("llq.owner",       "Owner",        "Owner",
                                         record_parser.DetailLabelParser, ("Owner",),
                                         value_saver.StringSaver,    ()),
            query_category.QueryCategory("llq.class",       "Class",        "Class",
                                         record_parser.DetailLabelParser, ("Class",),
                                         value_saver.StringSaver,    ()),
            query_category.QueryCategory("llq.job_script",  "Job Script",   "Cmd",
                                         record_parser.DetailLabelParser, ("Cmd",),
                                         value_saver.StringSaver,    ()),
            query_category.QueryCategory("llq.status",      "Status",       "Status",
                                         record_parser.DetailLabelParser, ("Status",),
                                         value_saver.JobStatusSaver, ())
        ])

        self.assertEqual(len(category_list), 5)

        self.assertEqual(category_list.index_from_id("llq.id"), 0)
        self.assertEqual(category_list.index_from_id("llclass.id"), -1)
        self.assertTrue(category_list.contains_id("llq.id"))
        self.assertFalse(category_list.contains_id("llclass.id"))
        self.assertEqual(category_list.category_from_id("llq.id").id, "llq.id")
        self.assertIsNone(category_list.category_from_id("llclass.id"))

        self.assertEqual(category_list.index_from_label("Class"), 2)
        self.assertTrue(category_list.contains_label("Class"))
        self.assertEqual(category_list.category_from_label("Class").id, "llq.class")
