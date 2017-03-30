import os
from nwpc_work_flow_model.sms.sms_node import SmsNode


class TestSmsNode(object):
    def test_normal_suite_cdp_output(self):
        with open(os.path.dirname(__file__) + "/data/cdp/normal_suite_cdp.txt") as f:
            cdp_output = f.readlines()
            node = SmsNode.create_from_cdp_output(cdp_output)
            assert node.get_variable_value('SUITE') == 'grapes_meso_v4_1'
            assert node.get_variable_value('DATE') == '15.01.2017'
            assert node.get_variable_value('DAY') == 'sunday'
            assert node.get_variable_value('DD') == '15'

            assert node.get_variable_value('SMSOUT') == '/cma/g1/nwp/SMSOUT'
            assert node.get_variable_value('SMSHOME') == '/cma/g1/nwp/SMSOUT'
            assert node.get_variable_value('VERSION') == '_v4_1'

    def test_normal_family_cdp_output(self):
        with open(os.path.dirname(__file__) + "/data/cdp/normal_family_cdp.txt") as f:
            cdp_output = f.readlines()
            node = SmsNode.create_from_cdp_output(cdp_output)
            assert node.get_variable_value('FAMILY') == 'cold'
            assert node.get_variable_value('FAMILY1') == 'cold'

            assert node.get_variable_value('SMSINCLUDE') == '/cma/u/nwp/smsworks/def/grapes_meso/include'
            assert node.get_variable_value('SMSFILES') == '/cma/u/nwp/smsworks/def/grapes_meso/smsfiles'

    def test_error_login_cdp(self):
        with open(os.path.dirname(__file__) + "/data/cdp/error_login_cdp.txt") as f:
            cdp_output = f.readlines()
            node = SmsNode.create_from_cdp_output(cdp_output)
            assert node is None

    def test_error_node_path_cdp(self):
        with open(os.path.dirname(__file__) + "/data/cdp/error_node_path_cdp.txt") as f:
            cdp_output = f.readlines()
            node = SmsNode.create_from_cdp_output(cdp_output)
            assert node is None

    def test_error_sms_server_cdp(self):
        with open(os.path.dirname(__file__) + "/data/cdp/error_sms_server_cdp.txt") as f:
            cdp_output = f.readlines()
            node = SmsNode.create_from_cdp_output(cdp_output)
            assert node is None
