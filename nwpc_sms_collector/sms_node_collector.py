import argparse
import datetime
import json
import subprocess
from nwpc_work_flow_model.sms.sms_node import SmsNode


def variable_handler(args):
    request_date_time = datetime.datetime.now()
    request_time_string = request_date_time.strftime("%Y-%m-%d %H:%M:%S")

    command_string = "login {sms_server} {sms_user} {sms_password}; status; show -f -K {node_path};exit".format(
        sms_server=args.sms_server,
        sms_user=args.sms_user,
        sms_password=args.sms_password,
        node_path=args.node_path
    )
    echo_pipe = subprocess.Popen(
        ['echo', command_string],
        stdout=subprocess.PIPE,
        encoding='utf-8'
    )
    cdp_pipe = subprocess.Popen(
        ['/cma/u/app/sms/bin/cdp'],
        stdin=echo_pipe.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8'
    )
    echo_pipe.stdout.close()
    (cdp_output, cdp_error) = cdp_pipe.communicate()

    cdp_output = cdp_output.splitlines(keepends=True)
    node = SmsNode.create_from_cdp_output(cdp_output)
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
                        'output': cdp_output,
                        'error_output': cdp_error
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

    subparsers = parser.add_subparsers(help="sub command help")

    parser_variable = subparsers.add_parser('variable', help='get variable from sms server')
    parser_variable.add_argument('--sms-server', type=str, help='sms server', required=True)
    parser_variable.add_argument('--sms-user', type=str, help='sms user', required=True)
    parser_variable.add_argument('--sms-password', type=str, help='sms password')
    parser_variable.add_argument('--node-path', type=str, help='node path', required=True)
    parser_variable.set_defaults(func=variable_handler)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
