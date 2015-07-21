import argparse
import os
import subprocess
import re
from datetime import datetime, time, timedelta
import json

import requests


def get_sms_status(sms_name, sms_user, sms_password):
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
                print "LINE: ",a_status_line.split()
            else:
                g = m2.groups()
                node_name = g[0]
                node_path = "/{node_name}".format(sms_name=sms_name, node_name=node_name)
                node_status = g[2]
                node_status_list.append({
                    'name': node_name,
                    'path': node_path,
                    'status': node_status
                })
                print "  |-",g[2], g[0]

        else:
            g = m.groups()
            print "/{sms_name}".format(sms_name=sms_name), g[1]
            node_name = sms_name
            node_path = "/"
            node_status = g[1]
            node_status_list.append({
                'name': node_name,
                'path': node_path,
                'status': node_status
            })

            print "  |-",g[5], g[3]
            node_name = g[3]
            node_path = "/{node_name}".format(sms_name=sms_name, node_name=node_name)
            node_status = g[5]
            node_status_list.append({
                'name': node_name,
                'path': node_path,
                'status': node_status
            })

    current_time = datetime.now().isoformat()
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

    args = parser.parse_args()

    sms_name = args.name
    sms_user = args.user
    sms_password = "1"
    if args.password:
        sms_password = args.password

    result = get_sms_status(sms_name, sms_user, sms_password)

    post_data = {
        'message': json.dumps(result)
    }

    print result

    if not args.disable_post:
        host = "10.28.32.175"
        port = 5101
        url = "http://{host}:{port}/api/v1/hpc/sms/status".format(host=host, port=port)
        requests.post(url, data=post_data)


if __name__ == "__main__":
    sms_status_command_line_tool()
