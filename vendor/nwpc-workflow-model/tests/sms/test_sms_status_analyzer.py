import os

from nwpc_workflow_model.sms import NodeStatus, NodeType
from nwpc_workflow_model.sms.sms_status_analyzer import SmsStatusAnalyzer


class TestSmsStatusAnalyzer:
    @classmethod
    def setup_class(cls):
        pass

    def test_normal_suite(self):
        with open(os.path.dirname(__file__) + "/data/cdp/status/normal_status.txt") as f:
            cdp_output = f.readlines()
            analyzer = SmsStatusAnalyzer()
            bunch = analyzer.analyse_node_status(cdp_output)

            node = bunch.find_node("/Web_post")
            assert node is not None
            assert node.status == NodeStatus.Queued
            assert node.get_node_type() == NodeType.Suite

            node = bunch.find_node("/Web_post/checker/GRAPES_MESO/12/00")
            assert node is not None
            assert node.status == NodeStatus.Complete
            assert node.get_node_type() == NodeType.Family

            node = bunch.find_node("/Web_post/checker/GRAPES_MESO/12/01/get_result_00")
            assert node is not None
            assert node.status == NodeStatus.Complete
            assert node.get_node_type() == NodeType.Task

            node = bunch.find_node("/Web_post/checker/GRAPES_MESO/00/11/get_result_00")
            assert node is not None
            assert node.status == NodeStatus.Queued
            assert node.get_node_type() == NodeType.Task
