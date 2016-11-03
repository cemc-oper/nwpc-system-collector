# coding=utf-8
import argparse
import datetime
import json
import os
import sys
import subprocess

import requests

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from nwpc_hpc_collector.loadleveler import QueryCategory, QueryCategoryList, QueryModel, QueryProperty, QueryItem
from nwpc_hpc_collector.loadleveler import record_parser
from nwpc_hpc_collector.loadleveler import value_saver
from nwpc_hpc_collector.util import json_default

config_file_name = "loadleveler_status.develop.config"
default_config_file_path = os.path.join(os.path.dirname(__file__), "conf", config_file_name)


def build_category_list(category_list_config):
    category_list = QueryCategoryList()
    for an_item in category_list_config:
        category = QueryCategory(
            category_id=an_item['id'],
            display_name=an_item['display_name'],
            label=an_item['display_name'],
            record_parser_class=getattr(record_parser, an_item['record_parser_class']),
            record_parser_arguments=tuple(an_item['record_parser_arguments']),
            value_saver_class=getattr(value_saver, an_item['value_saver_class']),
            value_saver_arguments=tuple(an_item['value_saver_arguments'])
        )
        category_list.append(category)
    return category_list


def run_llq_detail_command() -> str:
    command = "/usr/bin/llq -l"
    pipe = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    output = pipe.communicate()[0]
    output_string = output.decode()
    return output_string


def get_llq_detail_query_response(config):
    output_lines = run_llq_detail_command().split("\n")
    category_list = build_category_list(config['category_list'])

    model = QueryModel.build_from_category_list(output_lines, category_list)
    model_dict = model.to_dict()
    return model_dict


def get_config(config_file_path):
    """
    读取配置文件信息，配置文件为 json 格式
    :param config_file_path:
    :return:
    """
    config = None
    with open(config_file_path, 'r') as f:
        config = json.load(f)
    return config


def collect_handler(args):
    if args.config:
        config_file_path = args.config
    else:
        config_file_path = default_config_file_path
    config = get_config(config_file_path)

    response = get_llq_detail_query_response(config)

    result = {
        'app': 'nwpc_hpc_collector.loadleveler_status',
        'type': 'command',
        'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'data': {
            'request': {
                'sub_command': args.sub_command,
            },
            'response': response
        }
    }

    post_data = {
        'message': json.dumps(result, default=json_default)
    }
    # print(json.dumps(result, default=json_default, indent=4))

    if not args.disable_post:
        print("Posting loadleveler status...")
        host = config['post']['host']
        port = config['post']['port']
        url = config['post']['url'].format(host=host, port=port)
        response = requests.post(url, data=post_data)
        print("Posting loadleveler status...done ", response)


def loadleveler_status_command_line_tool():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
    DESCRIPTION
        Get loadleveler status using loadleveler CLI.""")

    sub_parsers = parser.add_subparsers(title="sub commands", dest="sub_command")

    collect_parser = sub_parsers.add_parser('collect', description="collect llq command result.")
    collect_parser.add_argument("--disable-post", help="disable post to agent.", action='store_true')
    collect_parser.add_argument(
        "-c", "--config",
        help="config file, default config file is ./conf/{config_file_name}".format(
            config_file_name=config_file_name
        )
    )

    args = parser.parse_args()
    if args.sub_command == "collect":
        collect_handler(args)

if __name__ == "__main__":
    loadleveler_status_command_line_tool()
