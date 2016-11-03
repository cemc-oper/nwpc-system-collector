# coding=utf-8
import unittest
from unittest import mock
import os
import importlib
import copy

from nwpc_hpc_collector.loadleveler import record_parser


class TestRecordParser(unittest.TestCase):
    def setUp(self):
        importlib.reload(record_parser)

    def tearDown(self):
        pass

    def test_deep_copy(self):
        parser_one = record_parser.DetailLabelParser("label-1")
        parser_two = copy.deepcopy(parser_one)
        parser_two.label = "label-2"
        self.assertNotEqual(parser_one.label, parser_two.label)

    def check_llq_detail_query_record_parser(self, test_case):
        lines = test_case["lines"]
        label = test_case["label"]
        value = test_case["value"]
        name = test_case["name"]

        parser = record_parser.DetailLabelParser(label)
        parser_value = parser.parse(lines)
        self.assertEqual(parser_value, value)
        print("Test passed:", name)

    def test_llq_detail_query_record_parser(self):
        serial_job_running_file_path = os.path.join(
            os.path.dirname(__file__),
            "../data/detail_query/llq/serial_job_running.txt"
        )
        test_case_list = []
        with open(serial_job_running_file_path) as serial_job_running_file:
            lines = serial_job_running_file.readlines()
            test_case_list.extend([
                {
                    "name": "llq.serial_job.running.job_step_id",
                    "lines": lines,
                    "label": "Job Step Id",
                    "value": "cma20n04.2882680.0"
                },
                {
                    "name": "llq.serial_job.running.cmd",
                    "lines": lines,
                    "label": "Cmd",
                    "value": "/cma/g1/nwp/SMSOUT/gmf_grapes_gfs_v2_0/grapes_global/12/post/postp_240.job1"
                },
                {
                    "name": "llq.serial_job.running.queue_date",
                    "lines": lines,
                    "label": "Queue Date",
                    "value": "Thu Sep  8 00:09:02 2016"
                },
                {
                    "name": "llq.serial_job.running.cpu_per_core",
                    "lines": lines,
                    "label": "Cpus Per Core",
                    "value": "0"
                },
                {
                    "name": "llq.serial_job.running.task_affinity",
                    "lines": lines,
                    "label": "Task Affinity",
                    "value": ""
                },
            ])

        for a_test_case in test_case_list:
            self.check_llq_detail_query_record_parser(a_test_case)

    def check_llq_script_record_parser(self, test_case):
        lines = test_case["lines"]
        value = test_case["value"]
        name = test_case["name"]

        parser = record_parser.LlqJobScriptParser()
        parser_value = parser.parse(lines)
        self.assertEqual(parser_value, value)
        print("Test passed:", name)

    def test_llq_script_record_parser(self):
        check_method = self.check_llq_script_record_parser
        serial_job_running_file_path = os.path.join(
            os.path.dirname(__file__),
            "../data/detail_query/llq/serial_job_running.txt"
        )
        test_case_list = []
        with open(serial_job_running_file_path) as serial_job_running_file:
            lines = serial_job_running_file.readlines()
            test_case_list.extend([
                {
                    "name": "llq.serial_job.running.job_script",
                    "lines": lines,
                    "value": "/cma/g1/nwp/SMSOUT/gmf_grapes_gfs_v2_0/grapes_global/12/post/postp_240.job1"
                }
            ])

        parallel_job_running_file_path = os.path.join(
            os.path.dirname(__file__),
            "../data/detail_query/llq/parallel_job_running.txt"
        )
        with open(parallel_job_running_file_path) as parallel_job_running_file:
            lines = parallel_job_running_file.readlines()
            test_case_list.extend([
                {
                    "name": "llq.parallel_job.running.job_script",
                    "lines": lines,
                    "value": "/cma/g1/nwp_qu/SMSOUT/rafs/cold/00/model/fcst.job1"
                }
            ])

        for a_test_case in test_case_list:
            check_method(a_test_case)
