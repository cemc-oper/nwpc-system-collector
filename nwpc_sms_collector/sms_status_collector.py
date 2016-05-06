# coding=utf-8
import argparse
import os
import subprocess
import re
from datetime import datetime, time, timedelta
import json

import requests


config_file_name = 'sms_status_collector.config'

SMS_STATUS_POST_HOST = "10.28.32.175"
SMS_STATUS_POST_PORT = 5101
SMS_STATUS_POST_URL = "http://{host}:{port}/api/v1/hpc/sms/status"


default_sms_variable_list = [
    {
        'variable_name': 'SMSDATE',
        'variable_pattern': r"^.*SMSDATE '([0-9]+)'", # TODO: gen var or edit var
        'variable_value_group_index': 0
    }
]


def get_config(config_file_path):
    """
    读取配置文件信息，配置文件为 json 格式
    :param config_file_path:
    :return:
    """
    global SMS_STATUS_POST_HOST, SMS_STATUS_POST_PORT, SMS_STATUS_POST_URL
    f = open(config_file_path, 'r')
    config = json.load(f)
    f.close()

    SMS_STATUS_POST_HOST = config['post']['host']
    SMS_STATUS_POST_PORT = config['post']['port']
    SMS_STATUS_POST_URL = config['post']['url']

    return config


def get_sms_variable(sms_name, sms_user, sms_password, node_path, variable_list=default_sms_variable_list):
    """
    获取 node_path 节点的变量
    :param sms_name:
    :param sms_user:
    :param sms_password:
    :param node_path: 节点路径，形如 /obs_reg
    :param variable_list: 变量列表
    :return:
    """
    command_string = "login {sms_name} {sms_user}  {sms_password};status;show -f -K {node_path};quit".format(
        sms_name=sms_name,
        sms_user=sms_user,
        sms_password=sms_password,
        node_path=node_path
    )
    echo_pipe = subprocess.Popen(['echo', command_string], stdout=subprocess.PIPE)
    cdp_pipe = subprocess.Popen(['/cma/u/app/sms/bin/cdp'],
                                stdin=echo_pipe.stdout,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    echo_pipe.stdout.close()
    (cdp_output, cdp_error) = cdp_pipe.communicate()
    return_code = cdp_pipe.returncode
    if return_code <> 0:
        current_time = datetime.now().isoformat()
        result = {
            'app': 'sms_status_collector',
            'timestamp': current_time,
            'error': 'command_return_code_error',
            'error-msg': cdp_error
        }
        return result
    cdp_output_lines = cdp_output.split('\n')

    variable_map = {}

    for a_variable in variable_list:
        a_variable['re_line'] = re.compile(a_variable['variable_pattern'])

    for line in cdp_output_lines:
        for a_variable in variable_list:
            m = a_variable['re_line'].match(line)
            if m is not None:
                g = m.groups()
                variable_value = g[a_variable['variable_value_group_index']]
                variable_map[a_variable['variable_name']] = variable_value
    return variable_map


def get_sms_status(sms_name, sms_user, sms_password, verbose=False):
    """
    获取 sms 服务器状态
    :param sms_name:
    :param sms_user:
    :param sms_password:
    :param verbose:
    :return:
    """
    command_string = "login {sms_name} {sms_user}  {sms_password};status;quit".format(
        sms_name=sms_name,
        sms_user=sms_user,
        sms_password=sms_password
    )
    echo_pipe = subprocess.Popen(['echo', command_string], stdout=subprocess.PIPE)
    cdp_pipe = subprocess.Popen(['/cma/u/app/sms/bin/cdp'],
                                stdin=echo_pipe.stdout,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    echo_pipe.stdout.close()
    (cdp_output, cdp_error) = cdp_pipe.communicate()
    # print cdp_output
    return_code = cdp_pipe.returncode
    if return_code <> 0:
        current_time = datetime.now().isoformat()
        result = {
            'app': 'sms_status_collector',
            'timestamp': current_time,
            'error': 'command_return_code_error',
            'error-msg': cdp_error
        }
        return result

    cdp_output_lines = cdp_output.split('\n')

    status_lines = []
    for line in cdp_output_lines:
        if line.startswith('Welcome') or line.startswith('#') or line=='' or line.startswith('Goodbye'):
            #print "[ ] ", line
            pass
        else:
            status_lines.append(line)
            #print "[x] ", line

    first_line = re.compile(r"^/(\[|\{)([a-z]+)(\]|\}) *([a-zA-z0-9_]*) *(\[|\{)([a-z]+)(\]|\}) *")
    none_first_line = re.compile(r"^ *([a-zA-z0-9_]*) *(\[|\{)([a-z]+)(\]|\}) *")

    node_status_list = []
    for a_status_line in status_lines:
        m = first_line.match(a_status_line)
        if m is None:
            m2 = none_first_line.match(a_status_line)
            if m2 is None:
                if verbose:
                    print "LINE: ",a_status_line.split()
            else:
                g = m2.groups()
                node_name = g[0]
                node_path = "/{node_name}".format(sms_name=sms_name, node_name=node_name)
                node_status = g[2]
                node_status_list.append({
                    'name': node_name,
                    'path': node_path,
                    'status': node_status,
                    'node_type': 'suite'
                })
                if verbose:
                    print "  |-",g[2], g[0]

        else:
            g = m.groups()
            if verbose:
                print "/{sms_name}".format(sms_name=sms_name), g[1]
            node_name = sms_name
            node_path = "/"
            node_status = g[1]
            node_status_list.append({
                'name': node_name,
                'path': node_path,
                'status': node_status,
                'node_type': 'server'
            })

            if verbose:
                print "  |-",g[5], g[3]
            node_name = g[3]
            node_path = "/{node_name}".format(sms_name=sms_name, node_name=node_name)
            node_status = g[5]
            node_status_list.append({
                'name': node_name,
                'path': node_path,
                'status': node_status,
                'node_type': 'suite'
            })

    for a_node_status in node_status_list:
        if a_node_status['node_type'] == 'suite':
            # print 'suite:',a_node_status['path']
            variable_result = get_sms_variable(sms_name, sms_user, sms_password, a_node_status['path'])
            if 'error' in variable_result:
                continue
            else:
                a_node_status['variable'] = variable_result

    current_time = (datetime.now() + timedelta(hours=8)).isoformat() # 北京时间
    result = {
        'app': 'sms_status_collector',
        'type': 'sms_status',
        'timestamp': current_time,
        'data': {
            'sms_name': sms_name,
            'sms_user': sms_user,
            'time': current_time,
            'status': node_status_list
        }
    }
    return result


def sms_status_command_line_tool():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
DESCRIPTION
    Get sms suites' status.""")

    parser.add_argument("-n", "--name", help="sms server name", required=True)
    parser.add_argument("-u", "--user", help="sms server user name", required=True)
    parser.add_argument("-p", "--password", help="sms server password")
    parser.add_argument("--disable-post", help="disable post to agent.", action='store_true')
    parser.add_argument("--verbose", help="show more outputs", action='store_true')
    parser.add_argument("-c", "--config", help="config file, default config file is ./conf/{config_file_name}".format(
        config_file_name=config_file_name
    ))

    args = parser.parse_args()

    # BUG: There is a bug for os.path.dirname on the python compiled by me on AIX.
    # config_file_path = os.path.dirname(__file__) + "/" + config_file_name
    config_file_path = "./conf/" + config_file_name

    if args.config:
        config_file_path = args.config
    get_config(config_file_path)

    sms_name = args.name
    sms_user = args.user
    sms_password = "1"
    verbose = False
    if args.password:
        sms_password = args.password
    if args.verbose:
        verbose = True

    result = get_sms_status(sms_name, sms_user, sms_password)

    post_data = {
        'message': json.dumps(result)
    }

    if verbose:
        print result
    print 'Get sms status...Done'

    if not args.disable_post:
        host = SMS_STATUS_POST_HOST
        port = SMS_STATUS_POST_PORT
        url = SMS_STATUS_POST_URL.format(host=host, port=port)
        requests.post(url, data=post_data)


if __name__ == "__main__":
    sms_status_command_line_tool()
