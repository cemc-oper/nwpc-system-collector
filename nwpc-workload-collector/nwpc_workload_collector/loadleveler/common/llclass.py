# coding: utf-8

from paramiko import SSHClient

from nwpc_hpc_model.workload.loadleveler import LoadLevelerQueryModel
from nwpc_workload_collector.loadleveler.common.model_util import build_category_list
from nwpc_workload_collector.base.model_util import sort_items
from nwpc_workload_collector.base.run import run_command


def sort_query_response_items(items, sort_keys=None):
    if sort_keys is None:
        sort_keys = ('status', 'queue_date')
    sort_keys = ['llq.'+i for i in sort_keys]
    sort_items(items, sort_keys)


def run_llclass_command(client: SSHClient, command="/usr/bin/llclass -l", params="") -> (str, str):
    """
    :param client: ssh client
    :param command:
    :param params:
    :return: command result string
    """
    return run_command(client, command + " " + params)


def get_llclass_query_model(client: SSHClient, config, params=""):
    """
    get response of llq query.

    :param client: SSH clinet
    :param config: config dict
        {
            category_list: a list of categories
                [
                    {
                        id: "llq.id",
                        display_name: "Id",
                        label: "Job Step Id",
                        record_parser_class: "DetailLabelParser",
                        record_parser_arguments: ["Job Step Id"],
                        value_saver_class: "StringSaver",
                        value_saver_arguments: []
                    }
                ]
    :param params:
    :return: model, see nwpc_hpc_model.workflow.query_model.QueryModel

    """
    std_out_string, std_error_out_string = run_llclass_command(client, params=params)
    output_lines = std_out_string.split("\n")
    category_list = build_category_list(config['llclass']['category_list'])

    model = LoadLevelerQueryModel.build_from_category_list(output_lines, category_list)
    return model
