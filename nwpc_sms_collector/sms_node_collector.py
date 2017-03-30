import argparse
import datetime
from paramiko import SSHClient, AutoAddPolicy
import json
import os
import sys


def variable_handler(args):
    request_date_time = datetime.datetime.now()
    request_time_string = request_date_time.strftime("%Y-%m-%d %H:%M:%S")

    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(args.host, args.port, args.user, args.password)

    command = 'echo "login {sms_server} {sms_user} {sms_password}; status; show -f -K {node_path};exit" |' \
              ' /cma/u/app/sms/bin/cdp'\
        .format(
            sms_server=args.sms_server,
            sms_user=args.sms_user,
            sms_password=args.sms_password,
            node_path=args.node_path
        )

    stdin, stdout, stderr = client.exec_command(command)
    std_out_string = stdout.read().decode('UTF-8')
    std_error_out_string = stderr.read().decode('UTF-8')
    client.close()

    cdp_output = std_out_string.splitlines(True)
    node = get_sms_node_from_cdp_output(cdp_output)
    if node is None:
        result = {
            'app': 'nwpc-sms-collector',
            'type': 'sms_collector',
            'error': 'variable-handler-error',
            'data': {
                'request': {
                    'command': 'variable',
                    'arguments': [],
                    'time': request_time_string
                },
                'response': {
                    'message': {
                        'output': std_out_string,
                        'error_output': std_error_out_string
                    },
                    'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
        print(json.dumps(result, indent=2))
    else:
        result = {
            'app': 'nwpc-sms-collector',
            'type': 'sms_collector',
            'data': {
                'request': {
                    'command': 'variable',
                    'arguments': [],
                    'time': request_time_string
                },
                'response': {
                    'node': node.to_dict(),
                    'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
        print(json.dumps(result, indent=2))
    return


def main():
    parser = argparse.ArgumentParser(prog="sms_collector")

    login_parser = argparse.ArgumentParser(add_help=False)
    login_parser.add_argument('-H', '--host', type=str, help='remote host', required=True)
    login_parser.add_argument('-P', '--port', type=int, help='remote host\'s port', default=22)
    login_parser.add_argument('-u', '--user', type=str, help='user', required=True)
    login_parser.add_argument('-p', '--password', type=str, help='password', required=True)

    subparsers = parser.add_subparsers(help="sub command help")

    parser_variable = subparsers.add_parser('variable', help='get variable from sms server', parents=[login_parser])
    parser_variable.add_argument('--sms-server', type=str, help='sms server', required=True)
    parser_variable.add_argument('--sms-user', type=str, help='sms user', required=True)
    parser_variable.add_argument('--sms-password', type=str, help='sms password')
    parser_variable.add_argument('--node-path', type=str, help='node path', required=True)
    parser_variable.set_defaults(func=variable_handler)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
