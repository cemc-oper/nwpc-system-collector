import os
from nwpc_sms_collector import sms_node_collector
from nwpc_work_flow_model.sms.sms_node import SmsNode
from nwpc_work_flow_model.sms.node_type import NodeType


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
    output_file = os.path.join(os.path.dirname(__file__), 'data/normal_suite_cdp_output.txt')
    output_error_file = os.path.join(os.path.dirname(__file__), 'data/normal_suite_cdp_output_error.txt')

    args = ArgObject()
    args.sms_server = "nwpc_wangdp"
    args.sms_user = "wangdp"
    args.sms_password = "1"
    args.node_path = "/windroc_info"

    monkeypatch.setattr(
        sms_node_collector,
        'get_cdp_output',
        generate_get_cdp_output_mock(output_file, output_error_file)
    )

    result = sms_node_collector.variable_handler(args)

    node_dict = result['data']['response']['node']
    node = SmsNode.create_from_dict(node_dict)

    assert node.name == 'windroc_info'
    assert node.node_type == 'suite'
    assert len(node.variable_list) == 8
    assert len(node.generated_variable_list) == 12
