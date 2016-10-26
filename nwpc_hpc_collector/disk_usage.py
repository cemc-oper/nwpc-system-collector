import subprocess
import os
import re
import locale
import argparse
import json
import datetime
import requests


def get_user_name() -> str:
    if 'USER' in os.environ:
        return os.environ["USER"]
    else:
        cmquota_command = "whoami"
        pipe = subprocess.Popen([cmquota_command], stdout=subprocess.PIPE, shell=True)
        return pipe.communicate()[0].decode().rstrip()


def run_cmquota_command() -> str:
    cmquota_command = "/cma/u/app/sys_bin/cmquota ${USER}"
    pipe = subprocess.Popen([cmquota_command], stdout=subprocess.PIPE, shell=True)
    output = pipe.communicate()[0]
    output_string = output.decode()
    return output_string


def get_cmquota() -> dict:
    user = get_user_name()
    result_lines = run_cmquota_command().split("\n")

    detail_pattern = r'^(\w+) +(\w+) +(\d+) +(\d+) +(\d+) +(\d+) +(\w+) \| +(\d+) +(\d+) +(\d+) +(\d+) +(\w+) +(\w+)'
    detail_prog = re.compile(detail_pattern)
    quota_result = dict()
    file_system_list = list()

    for a_line in result_lines:
        detail_re_result = detail_prog.match(a_line)
        if detail_re_result:
            file_system = detail_re_result.group(1)
            quota_type = detail_re_result.group(2)

            current_usage = detail_re_result.group(3)
            if current_usage.isdigit():
                current_usage = locale.atoi(current_usage)

            block_quota = detail_re_result.group(4)
            if block_quota.isdigit():
                block_quota = locale.atoi(block_quota)

            block_limit = detail_re_result.group(5)
            if block_limit.isdigit():
                block_limit = locale.atoi(block_limit)

            block_in_doubt = detail_re_result.group(6)
            if block_in_doubt.isdigit():
                block_in_doubt = locale.atoi(block_in_doubt)

            block_grace = detail_re_result.group(7)

            file_files = detail_re_result.group(8)
            if file_files.isdigit():
                file_files = locale.atoi(file_files)

            file_quota = detail_re_result.group(9)
            if file_quota.isdigit():
                file_quota = locale.atoi(file_quota)

            file_limit = detail_re_result.group(10)
            if file_limit.isdigit():
                file_limit = locale.atoi(file_limit)

            file_in_doubt = detail_re_result.group(11)
            if file_in_doubt.isdigit():
                file_in_doubt = locale.atoi(file_in_doubt)

            file_grace = detail_re_result.group(12)
            file_remarks = detail_re_result.group(13)

            current_file_system = dict()
            current_file_system['file_system'] = file_system
            current_file_system['type'] = quota_type

            block_limits = {
                'current': current_usage,
                'quota': block_quota,
                'limit': block_limit,
                'in_doubt': block_in_doubt,
                'grace': block_grace
            }
            file_limits = {
                'files': file_files,
                'quota': file_quota,
                'limit': file_limit,
                'in_doubt': file_in_doubt,
                'grace': file_grace,
                'remarks': file_remarks
            }
            current_file_system['block_limits'] = block_limits
            current_file_system['file_limits'] = file_limits

            file_system_list.append(current_file_system)

    quota_result['file_systems'] = file_system_list
    quota_result['user'] = user
    return quota_result


config_file_name = "disk_usage.develop.config"
default_config_file_path = os.path.join(os.path.dirname(__file__), "conf", config_file_name)


def get_config(config_file_path: str) -> dict:
    """
    读取配置文件信息，配置文件为 json 格式
    :param config_file_path:
    :return:
    """
    config = None
    with open(config_file_path, 'r') as f:
        config = json.load(f)
    return config


def disk_usage_command_show_handler(args):
    if args.config:
        config_file_path = args.config
    else:
        config_file_path = default_config_file_path
    config = get_config(config_file_path)

    cmquota_result = get_cmquota()
    result = {
        'app': 'nwpc_hpc_collector.disk_usage',
        'type': 'command',
        'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'data': {
            'request': {
                'sub_command': args.sub_command,
            },
            'response': cmquota_result
        }
    }
    print(json.dumps(result, indent=4))


def disk_usage_command_collect_handler(args):
    """
    通过 POST 发送 disk usage 到 agent:
        POST
            message: json string

    message 说明：
        {
            'app': 'nwpc_hpc_collector.disk_usage',
            'type': 'command',
            'time': '%Y-%m-%d %H:%M:%S',
            'data': {
            'request': {
                'sub_command': 'collect',
            },
            'response': cmquota_result
        }


    :param args:
    :return:
    """
    if args.config:
        config_file_path = args.config
    else:
        config_file_path = default_config_file_path
    config = get_config(config_file_path)

    cmquota_result = get_cmquota()
    result = {
        'app': 'nwpc_hpc_collector.disk_usage',
        'type': 'command',
        'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'data': {
            'request': {
                'sub_command': args.sub_command,
            },
            'response': cmquota_result
        }
    }
    user = cmquota_result['user']

    post_data = {
        'message': json.dumps(result)
    }

    if not args.disable_post:
        print("Posting sms status...")
        host = config['post']['host']
        port = config['post']['port']
        url = config['post']['url'].format(host=host, port=port, user=user)
        response = requests.post(url, data=post_data)
        print(response)
        print("Posting sms status...done")


def disk_usage_command_line_tool():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
    DESCRIPTION
        Get disk usage using cmquota command.""")

    sub_parsers = parser.add_subparsers(title="sub commands", dest="sub_command")

    show_parser = sub_parsers.add_parser('show', description="print cmquota command result.")
    show_parser.add_argument(
        "-c", "--config",
        help="config file, default config file is ./conf/{config_file_name}".format(
            config_file_name=config_file_name
        )
    )

    collect_parser = sub_parsers.add_parser('collect', description="collect cmquota command result.")
    collect_parser.add_argument("--disable-post", help="disable post to agent.", action='store_true')
    collect_parser.add_argument(
        "-c", "--config",
        help="config file, default config file is ./conf/{config_file_name}".format(
            config_file_name=config_file_name
        )
    )

    args = parser.parse_args()
    if args.sub_command == "show":
        disk_usage_command_show_handler(args)

    elif args.sub_command == "collect":
        disk_usage_command_collect_handler(args)


if __name__ == "__main__":
    disk_usage_command_line_tool()
