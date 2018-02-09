import os
from nwpc_sms_collector import sms_node_collector
from nwpc_workflow_model.sms.sms_node import SmsNode
from nwpc_workflow_model.sms.node_type import NodeType


class ArgObject(object):
    pass


def generate_get_cdp_output_mock(output_file, output_error_file):
    def mock_get_cdp_output(cdp_command_string):
        with open(output_file) as cdp_file:
            cdp_output = cdp_file.read()
        with open(output_error_file) as cdp_file:
            cdp_error = cdp_file.read()
        return cdp_output, cdp_error

    return mock_get_cdp_output


def test_variable_handler(monkeypatch):
    output_file = os.path.join(os.path.dirname(__file__), 'data/normal_suite_info_output.txt')
    output_error_file = os.path.join(os.path.dirname(__file__), 'data/normal_suite_info_output.txt')

    args = ArgObject()
    args.sms_server = "nwpc_op"
    args.sms_user = "nwp"
    args.sms_password = "1"
    args.node_path = "/grapes_meso_v4_1"

    monkeypatch.setattr(
        sms_node_collector,
        'get_cdp_output',
        generate_get_cdp_output_mock(output_file, output_error_file)
    )

    result = sms_node_collector.variable_handler(args)

    node_dict = result['data']['response']['node']
    node = SmsNode.create_from_dict(node_dict)

    assert node.name == 'grapes_meso_v4_1'
    assert node.node_type == 'suite'
    assert len(node.variable_list) == 3
    assert len(node.generated_variable_list) == 12
