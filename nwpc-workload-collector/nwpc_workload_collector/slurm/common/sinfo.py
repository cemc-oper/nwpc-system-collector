# coding: utf-8
import subprocess

from paramiko import SSHClient

from nwpc_workload_collector.base.model_util import sort_items
from nwpc_workload_collector.base.run import run_command
from nwpc_workload_collector.slurm.common.model_util import build_category_list
from nwpc_hpc_model.workload.slurm import SlurmQueryModel


def sort_query_response_items(items, sort_keys=None):
    if sort_keys is None:
        sort_keys = ('partition', )
    sort_keys = ['sinfo.'+i for i in sort_keys]
    sort_items(items, sort_keys)


def run_sinfo_command(client: SSHClient, config, params="") -> str:
    """
    :param client:
    :param config:
    :param params:
    :return: command result string
    """
    command = config['sinfo']['command']
    return run_command(client, command + " " + params)


def get_sinfo_query_model(client: SSHClient, config, params=""):
    """
    get response of sinfo query.

    :param client:
    :param config: config dict
    :param params:
    :return: model, see nwpc_hpc_model.workflow.query_model.QueryModel

    """
    std_out_string, std_error_out_string = run_sinfo_command(client, config, params=params)
    output_lines = std_out_string.split("\n")
    category_list = build_category_list(config['sinfo']['category_list'])

    model = SlurmQueryModel.build_from_table_category_list(output_lines, category_list)
    return model
