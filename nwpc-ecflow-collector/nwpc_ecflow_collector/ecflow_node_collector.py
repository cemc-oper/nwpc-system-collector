# coding=utf-8
import json
import datetime

import click
import ecflow

from nwpc_ecflow_collector.ecflow_util.node_util import get_node_variable


@click.group()
def cli():
    pass


@cli.command()
@click.option('--owner', '-o', help='owner name')
@click.option('--repo', '-r', help='repo name')
@click.option('--host', help='ecflow host, ECF_HOST')
@click.option('--port', help='ecflow port, ECF_PORT')
@click.option('--path', '-p', 'node_path', help='node path')
@click.option('--config', '-c', 'config_file_path', help='config file path')
def variable(owner, repo, host, port, node_path, config_file_path):
    request_date_time = datetime.datetime.utcnow()
    request_time_string = request_date_time.strftime("%Y-%m-%d %H:%M:%S")

    client = ecflow.Client(host, port)
    client.sync_local()
    defs = client.get_defs()

    if defs is None:
        result = {
            'app': 'nwpc-ecflow-collector',
            'type': 'ecflow_node_collector',
            'error': 'variable-error',
            'data': {
                'request': {
                    'command': 'variable',
                    'arguments': [],
                    'time': request_time_string
                },
                'response': {
                    'error': 'defs not found',
                    'time': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
        print(json.dumps(result, indent=2))
        return result

    node = defs.find_abs_node(node_path)
    if node is None:
        result = {
            'app': 'nwpc-ecflow-collector',
            'type': 'ecflow_node_collector',
            'error': 'variable-error',
            'data': {
                'request': {
                    'command': 'variable',
                    'arguments': [],
                    'time': request_time_string
                },
                'response': {
                    'error': 'node not found',
                    'time': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
        print(json.dumps(result, indent=2))
        return result

    ecf_node = get_node_variable(node)

    result = {
        'app': 'nwpc-ecflow-collector',
        'type': 'ecflow_node_collector',
        'data': {
            'request': {
                'command': 'variable',
                'arguments': [],
                'time': request_time_string
            },
            'response': {
                'node': ecf_node.to_dict(),
                'time': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    }
    print(json.dumps(result, indent=2))

    return result


if __name__ == "__main__":
    cli()
