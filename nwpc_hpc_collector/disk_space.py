import subprocess
import os
import re
import locale
import argparse
import json
import datetime
import gzip
import requests


config_file_name = "disk_space.develop.config"
default_config_file_path = os.path.join(os.path.dirname(__file__), "conf", config_file_name)


def run_df_command() -> str:
    cmquota_command = "/usr/bin/df -g"
    pipe = subprocess.Popen([cmquota_command], stdout=subprocess.PIPE, shell=True)
    output = pipe.communicate()[0]
    output_string = output.decode()
    return output_string


def get_disk_space() -> dict:
    result_lines = run_df_command().split("\n")

    detail_pattern = r'^(\S+) +(\S+) +(\S+) +(\S+) +(\S+) +(\S+) +(\S+)'
    detail_prog = re.compile(detail_pattern)
    quota_result = dict()
    file_system_list = list()

    for a_line in result_lines[1:]:
        detail_re_result = detail_prog.match(a_line)
        if detail_re_result:
            file_system = detail_re_result.group(1)

            gb_blocks = detail_re_result.group(2)
            if gb_blocks.isdigit():
                gb_blocks = locale.atoi(gb_blocks)

            free_disk_space = detail_re_result.group(3)
            if free_disk_space.isdigit():
                free_disk_space = locale.atoi(free_disk_space)

            space_used_percent = detail_re_result.group(4)
            if space_used_percent[-1] == '%':
                space_used_percent = space_used_percent[:-1]

            inode_used = detail_re_result.group(5)
            if inode_used.isdigit():
                inode_used = locale.atoi(inode_used)

            inode_used_percent = detail_re_result.group(6)
            if inode_used_percent[-1] == '%':
                inode_used_percent = inode_used_percent[:-1]

            mounted_on = detail_re_result.group(7)

            current_file_system = {
                'file_system': file_system,
                'gb_blocks': gb_blocks,
                'free_space': free_disk_space,
                'space_used_percent': space_used_percent,
                'inode_used': inode_used,
                'inode_used_percent': inode_used_percent,
                'mounted_on': mounted_on
            }

            file_system_list.append(current_file_system)

    quota_result['file_systems'] = file_system_list
    return quota_result


def get_config(config_file_path: str) -> dict:
    """
    read config file which is a json file
    :param config_file_path:
    :return:
    """
    config = None
    with open(config_file_path, 'r') as f:
        config = json.load(f)
    return config


def disk_space_command_show_handler(args):
    if args.config:
        config_file_path = args.config
    else:
        config_file_path = default_config_file_path
    config = get_config(config_file_path)

    disk_space_result = get_disk_space()
    result = {
        'app': 'nwpc_hpc_collector.disk_usage',
        'type': 'command',
        'time': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        'data': {
            'request': {
                'sub_command': args.sub_command,
            },
            'response': disk_space_result
        }
    }
    print(json.dumps(result, indent=4))


def disk_space_command_collect_handler(args):
    """
    use HTTP POST to send disk space to agent
        POST
            message: json string

    message：
        {
            'app': 'nwpc_hpc_collector.disk_space',
            'type': 'command',
            'time': '%Y-%m-%d %H:%M:%S',
            'data': {
            'request': {
                'sub_command': 'collect',
            },
            'response': df_result
        }


    :param args:
    :return:
    """
    if args.config:
        config_file_path = args.config
    else:
        config_file_path = default_config_file_path
    config = get_config(config_file_path)

    cmquota_result = get_disk_space()
    result = {
        'app': 'nwpc_hpc_collector.disk_space',
        'type': 'command',
        'time': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        'data': {
            'request': {
                'sub_command': args.sub_command,
            },
            'response': cmquota_result
        }
    }

    post_data = {
        'message': json.dumps(result)
    }

    if not args.disable_post:
        print("Posting disk space...")
        host = config['post']['host']
        port = config['post']['port']
        url = config['post']['url'].format(host=host, port=port)

        content_encoding = ''
        if 'headers' in config['post']:
            headers = config['post']['headers']
            if 'content-encoding' in headers:
                content_encoding = headers['content-encoding']

        if content_encoding == 'gzip':
            gzipped_post_data = gzip.compress(bytes(json.dumps(post_data), 'utf-8'))
            response = requests.post(url, data=gzipped_post_data, headers={
                'content-encoding': 'gzip'
            })
        else:
            response = requests.post(url, data=post_data)

        print(response)
        print("Posting disk space...done")


def disk_space_command_line_tool():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
    DESCRIPTION
        Get disk space using df command.""")

    sub_parsers = parser.add_subparsers(title="sub commands", dest="sub_command")

    show_parser = sub_parsers.add_parser('show', description="print df command result.")
    show_parser.add_argument(
        "-c", "--config",
        help="config file, default config file is ./conf/{config_file_name}".format(
            config_file_name=config_file_name
        )
    )

    collect_parser = sub_parsers.add_parser('collect', description="collect df command result.")
    collect_parser.add_argument("--disable-post", help="disable post to agent.", action='store_true')
    collect_parser.add_argument(
        "-c", "--config",
        help="config file, default config file is ./conf/{config_file_name}".format(
            config_file_name=config_file_name
        )
    )

    args = parser.parse_args()
    if args.sub_command == "show":
        disk_space_command_show_handler(args)

    elif args.sub_command == "collect":
        disk_space_command_collect_handler(args)


if __name__ == "__main__":
    disk_space_command_line_tool()
